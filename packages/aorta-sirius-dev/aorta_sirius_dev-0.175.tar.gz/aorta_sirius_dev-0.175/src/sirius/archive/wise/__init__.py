import datetime
import uuid
from _decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import List, Dict, Any, Union, cast

from pydantic import PrivateAttr, Field

from sirius import common
from sirius.archive.wise.exceptions import CashAccountNotFoundException, ReserveAccountNotFoundException, \
    RecipientNotFoundException
from sirius.common import DataClass, Currency
from sirius.communication.discord import AortaTextChannels, get_timestamp_string, \
    DiscordDefaults
from sirius.constants import EnvironmentSecret
from sirius.exceptions import OperationNotSupportedException
from sirius.http_requests import SyncHTTPSession, HTTPResponse
from sirius.http_requests.exceptions import HTTPException
from sirius.wise import constants


class WiseAccountType(Enum):
    PRIMARY = auto()
    SECONDARY = auto()


class TransactionType(Enum):
    CARD = "CARD"
    CONVERSION = "CONVERSION"
    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"
    MONEY_ADDED = "MONEY_ADDED"
    UNKNOWN = "UNKNOWN"


class WebhookAccountUpdateType(Enum):
    CREDIT = "balances#credit"
    UPDATE = "balances#update"
    STATE_CHANGE = "balances#account-state-change"


class WiseAccount(DataClass):
    type: WiseAccountType
    personal_profile: "PersonalProfile"
    business_profile: "BusinessProfile | None"
    _http_session: SyncHTTPSession = PrivateAttr()

    @property
    def http_session(self) -> SyncHTTPSession:
        return self._http_session

    def _initialize(self) -> None:
        if self.personal_profile is None or self.business_profile is None:
            profile_list: List[Profile] = Profile.get_all(self)
            self.personal_profile = cast(PersonalProfile, next(filter(lambda p: p.type.lower() == "personal", profile_list)))
            self.business_profile = cast(BusinessProfile, next((p for p in profile_list if p.type.lower() == "business"), None))
        else:
            self.personal_profile._initialize()
            if self.business_profile:
                self.business_profile._initialize()

    @staticmethod
    def get(wise_account_type: WiseAccountType) -> "WiseAccount":
        environmental_variable: EnvironmentSecret = EnvironmentSecret.WISE_PRIMARY_ACCOUNT_API_KEY if wise_account_type == WiseAccountType.PRIMARY else EnvironmentSecret.WISE_SECONDARY_ACCOUNT_API_KEY
        http_session: SyncHTTPSession = SyncHTTPSession(constants.URL, {
            "Authorization": f"Bearer {common.get_environmental_secret(environmental_variable)}"})

        wise_account: WiseAccount = WiseAccount.model_construct(type=wise_account_type, personal_profile=None,
                                                                business_profile=None)
        wise_account._http_session = http_session
        wise_account._initialize()

        WiseAccount.model_validate(wise_account)
        return wise_account


class Profile(DataClass):
    id: int
    type: str
    cash_account_list: List["CashAccount"] | None = None
    reserve_account_list: List["ReserveAccount"] | None = None
    recipient_list: List["Recipient"] | None = None
    debit_card_list: List["DebitCard"] | None = None
    wise_account: WiseAccount = Field(exclude=True)

    @property
    def http_session(self) -> SyncHTTPSession:
        return self.wise_account.http_session

    def _initialize(self) -> None:
        cash_account_to_update_list: List["CashAccount"] = CashAccount.get_all(self)
        reserve_account_to_update_list: List["ReserveAccount"] = ReserveAccount.get_all(self)
        recipient_to_update_list: List["Recipient"] = Recipient.get_all(self)

        if self.cash_account_list is None:
            self.cash_account_list = cash_account_to_update_list
        else:
            for original_cash_account in self.cash_account_list:
                try:
                    new_cash_account: CashAccount = next(
                        filter(lambda c: (c.id == original_cash_account.id), cash_account_to_update_list))
                    original_cash_account.__dict__.update(new_cash_account.model_dump())
                    cash_account_to_update_list.remove(new_cash_account)
                except StopIteration:
                    self.cash_account_list.remove(original_cash_account)

            [self.cash_account_list.append(new_cash_account) for new_cash_account in cash_account_to_update_list]  # type: ignore[func-returns-value]

        if self.reserve_account_list is None:
            self.reserve_account_list = reserve_account_to_update_list
        else:
            for original_reserve_account in self.reserve_account_list:
                try:
                    new_reserve_account: ReserveAccount = next(
                        filter(lambda r: (r.id == original_reserve_account.id), reserve_account_to_update_list))
                    original_reserve_account.__dict__.update(new_reserve_account.model_dump())
                    reserve_account_to_update_list.remove(new_reserve_account)
                except StopIteration:
                    self.reserve_account_list.remove(original_reserve_account)

            [self.reserve_account_list.append(new_reserve_account) for new_reserve_account in reserve_account_to_update_list]  # type: ignore[func-returns-value]

        if self.recipient_list is None:
            self.recipient_list = recipient_to_update_list
        else:
            for original_recipient in self.recipient_list:
                try:
                    new_recipient: Recipient = next(
                        filter(lambda r: (r.id == original_recipient.id), recipient_to_update_list))
                    original_recipient.__dict__.update(new_recipient.model_dump())
                    recipient_to_update_list.remove(new_recipient)
                except StopIteration:
                    self.recipient_list.remove(original_recipient)

            [self.recipient_list.append(new_recipient) for new_recipient in recipient_to_update_list]  # type: ignore[func-returns-value]

    def get_cash_account(self, currency: Currency, is_create_if_unavailable: bool = False) -> "CashAccount":
        try:
            return next(filter(lambda c: c.currency == currency, self.cash_account_list))
        except StopIteration:
            if is_create_if_unavailable:
                return CashAccount.open(self, currency)
            else:
                raise CashAccountNotFoundException(f"Currency not found: \n"
                                                   f"Profile: {self.__class__.__name__}"
                                                   f"Currency: {currency.value}")

    def get_reserve_account(self, account_name: str, currency: Currency,
                            is_create_if_unavailable: bool = False) -> "ReserveAccount":

        try:
            return next(filter(lambda r: r.name == account_name and r.currency == currency, self.reserve_account_list))
        except StopIteration:
            if is_create_if_unavailable:
                return ReserveAccount.open(self, account_name, currency)
            else:
                raise ReserveAccountNotFoundException(f"Currency not found: \n"
                                                      f"Profile: {self.__class__.__name__}"
                                                      f"Reserve Account Name: {account_name}")

    def get_recipient(self, account_number: str) -> "Recipient":

        try:
            return next(filter(lambda r: r.account_number == account_number, self.recipient_list))
        except StopIteration:
            raise RecipientNotFoundException(f"Recipient not found: \n"
                                             f"Profile: {self.__class__.__name__}"
                                             f"Account Number: {account_number}")

    @common.only_in_dev
    def _complete_all_transfers(self) -> None:
        for cash_account in self.cash_account_list:
            http_response: HTTPResponse = self.http_session.get(
                f"{constants.ENDPOINT__TRANSFER__GET_ALL.replace('$profileId', str(self.id))}&status=processing&createdDateStart=2021-01-01&limit=200")
            [cash_account._simulate_completed_transfer(data["id"]) for data in http_response.data]

    @staticmethod
    def get_all(wise_account: WiseAccount) -> List["Profile"]:
        http_response: HTTPResponse = wise_account.http_session.get(constants.ENDPOINT__PROFILE__GET_ALL)
        profile_list: List["Profile"] = []

        for data in http_response.data:
            profile: Profile = Profile(id=data["id"], type=data["type"], wise_account=wise_account)
            profile._initialize()
            profile_list.append(profile)

        return profile_list

    @common.only_in_dev
    async def _reset(self) -> None:
        self._complete_all_transfers()

        for reserve_account in self.reserve_account_list:
            await reserve_account._set_balance(Decimal("0"))
            reserve_account.close()

        [await cash_account._set_balance(Decimal("0")) for cash_account in self.cash_account_list]


class PersonalProfile(Profile):
    pass


class BusinessProfile(Profile):
    pass


class Transaction(DataClass):
    id: int | None
    account: "Account" = Field(exclude=True)
    timestamp: datetime.datetime
    type: TransactionType
    description: str
    amount: Decimal
    third_party: Union[str, "ReserveAccount", "Recipient"]


class Account(DataClass):
    id: int
    name: str | None
    currency: Currency
    balance: Decimal
    profile: Profile = Field(exclude=True)

    @property
    def http_session(self) -> SyncHTTPSession:
        return self.profile.http_session

    def close(self) -> None:
        if self.balance != Decimal("0"):
            raise OperationNotSupportedException(f"Cannot close account due to non-zero account balance:\n"
                                                 f"Account Name: {self.name}\n"
                                                 f"Currency: {self.currency.value}\n"
                                                 f"Balance: {'{:,}'.format(self.balance)}")

        self.http_session.delete(
            constants.ENDPOINT__BALANCE__CLOSE.replace("$profileId", str(self.profile.id)).replace("$balanceId",
                                                                                                   str(self.id)))
        self.profile.wise_account._initialize()

    def get_transactions(self, from_time: datetime.datetime | None = None, to_time: datetime.datetime | None = None,
                         number_of_past_hours: int | None = None) -> List["Transaction"]:
        number_of_past_hours = 24 if number_of_past_hours is None else number_of_past_hours
        if from_time is None:
            from_time = datetime.datetime.now() - datetime.timedelta(hours=number_of_past_hours)

        if to_time is None:
            to_time = datetime.datetime.now()

        response: HTTPResponse = self.http_session.get(
            constants.ENDPOINT__BALANCE__GET_TRANSACTIONS.replace("$profileId", str(self.profile.id)).replace(
                "$balanceId", str(self.id)), query_params={
                "currency": self.currency.value,
                "intervalStart": f"{from_time.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().split('+')[0]}Z",
                "intervalEnd": f"{to_time.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().split('+')[0]}Z",
                "type": "COMPACT"
            })

        transaction_list: List[Transaction] = []
        for data in response.data["transactions"]:
            transaction_type: TransactionType = TransactionType(data["details"]["type"])
            third_party: str | ReserveAccount | Recipient
            id: int | None

            try:
                id = int(data["referenceNumber"].replace("TRANSFER-", ""))
            except ValueError:
                id = None

            if transaction_type == TransactionType.DEPOSIT:
                third_party = data["details"]["senderName"] + " | " + data["details"]["senderAccount"]

            elif transaction_type == TransactionType.TRANSFER:
                try:
                    third_party = self.profile.get_recipient(data["details"]["recipient"]["bankAccount"])
                except RecipientNotFoundException:
                    third_party = data["details"]["recipient"]["name"] + " | " + data["details"]["recipient"][
                        "bankAccount"]

            elif transaction_type == TransactionType.CARD:
                third_party = data["details"]["merchant"]["name"] + " | " + data["details"]["merchant"]["country"]

            elif transaction_type == TransactionType.CONVERSION:
                description: str = data["details"]["description"]
                reserve_account_name: str = description.split(" to ")[1] if " to " in description else \
                    description.split(" from ")[1]
                try:
                    third_party = self.profile.get_reserve_account(reserve_account_name, self.currency)
                except ReserveAccountNotFoundException:
                    third_party = reserve_account_name

            transaction_list.append(Transaction(
                id=id,
                account=self,
                timestamp=data["date"],
                type=transaction_type,
                description=data["details"]["description"],
                amount=Decimal(str(data["amount"]["value"])),
                third_party=third_party
            ))

        return transaction_list

    @staticmethod
    def abstract_open(profile: Profile, account_name: str | None, currency: Currency,
                      is_reserve_account: bool) -> "Account":
        data = {
            "currency": currency.value,
            "type": "SAVINGS" if is_reserve_account else "STANDARD"
        }

        if is_reserve_account:
            data["name"] = account_name

        response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__BALANCE__OPEN.replace("$profileId", str(profile.id)), data=data,
            headers={"X-idempotence-uuid": str(uuid.uuid4())})
        return Account(
            id=response.data["id"],
            name=account_name,
            currency=currency,
            balance=Decimal("0"),
            profile=profile
        )


class CashAccount(Account):

    @common.only_in_dev
    def _simulate_completed_transfer(self, transfer_id: int) -> None:
        url: str = constants.ENDPOINT__SIMULATION__COMPLETE_TRANSFER.replace("$transferId", str(transfer_id))
        try:
            self.http_session.get(url.replace("$status", "processing"))
            self.http_session.get(url.replace("$status", "funds_converted"))
            self.http_session.get(url.replace("$status", "outgoing_payment_sent"))
        except HTTPException:
            pass

    async def transfer(self, to_account: Union["CashAccount", "ReserveAccount", "Recipient"], amount: Decimal,
                       reference: str | None = None, is_amount_in_from_currency: bool = False) -> "Transfer":
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if isinstance(to_account, ReserveAccount) and self.currency != to_account.currency:
            raise OperationNotSupportedException(
                "Direct inter-currency transfers from a cash account to a reserve account is not supported")

        transfer: Transfer = Transfer.model_construct()
        if isinstance(to_account, CashAccount):
            transfer = Transfer.intra_cash_account_transfer(self.profile, self, to_account, amount,
                                                            is_amount_in_from_currency)
            await DiscordDefaults.send_message(AortaTextChannels.WISE.value, f"**Intra-Account Transfer**:\n"
                                                                             f"Timestamp: {get_timestamp_string(datetime.datetime.now())}\n"
                                                                             f"From: *{self.currency.value}*\n"
                                                                             f"To: *{to_account.currency.value}*\n"
                                                                             f"Amount: *{self.currency.value} {'{:,}'.format(amount)}*\n"
                                               )

        elif isinstance(to_account, ReserveAccount):
            transfer = Transfer.cash_to_savings_account_transfer(self.profile, self, to_account, amount)
            await DiscordDefaults.send_message(AortaTextChannels.WISE.value, f"**Intra-Account Transfer**:\n"
                                                                             f"Timestamp: {get_timestamp_string(datetime.datetime.now())}\n"
                                                                             f"From: *{self.currency.value}*\n"
                                                                             f"To: *{to_account.name}*\n"
                                                                             f"Amount: *{self.currency.value} {'{:,}'.format(amount)}*\n")

        elif isinstance(to_account, Recipient):
            transfer = Transfer.cash_to_third_party_cash_account_transfer(self.profile, self, to_account, amount,
                                                                          "" if reference is None else reference,
                                                                          is_amount_in_from_currency)
            await DiscordDefaults.send_message(AortaTextChannels.WISE.value, f"**Third-Party Transfer**:\n"
                                                                             f"Timestamp: {get_timestamp_string(datetime.datetime.now())}\n"
                                                                             f"From: *{self.currency.value}*\n"
                                                                             f"To: *{to_account.account_holder_name}*\n"
                                                                             f"Amount: *{self.currency.value} {'{:,}'.format(amount)}*\n")

            if not common.is_production_environment():
                self._simulate_completed_transfer(transfer.id)

        self.profile.wise_account._initialize()
        Transfer.model_validate(transfer)
        return transfer

    @common.only_in_dev
    def _simulate_top_up(self, amount: Decimal) -> None:
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if not common.is_development_environment():
            raise OperationNotSupportedException("Simulations can only be done in a development environment")

        self.profile.http_session.post(constants.ENDPOINT__SIMULATION__TOP_UP, {
            "profileId": self.profile.id,
            "balanceId": self.id,
            "currency": self.currency.value,
            "amount": float(amount)
        })
        self.profile.wise_account._initialize()

    @common.only_in_dev
    async def _set_balance(self, amount: Decimal) -> None:
        if self.balance > amount:
            await self._set_maximum_balance(amount)
        else:
            self._set_minimum_balance(amount)

    @common.only_in_dev
    def _set_minimum_balance(self, amount: Decimal) -> None:
        if self.balance < amount:
            self._simulate_top_up(amount - self.balance)

    @common.only_in_dev
    async def _set_maximum_balance(self, amount: Decimal) -> None:
        if self.balance <= amount:
            return

        maximum_transfer_amount: Decimal = Decimal(500_000)
        amount_to_deduct: Decimal = min(self.balance - amount, maximum_transfer_amount)
        recipient: Recipient = self.profile.get_recipient("12345678901234")

        if amount_to_deduct < Decimal("10"):
            amount_to_deduct = amount_to_deduct + Decimal("10")
            self._set_minimum_balance(self.balance + Decimal("10"))

        await self.transfer(recipient, amount_to_deduct, is_amount_in_from_currency=True)

        if self.balance > amount:
            await self._set_maximum_balance(amount)

    @staticmethod
    def get_all(profile: Profile) -> List["CashAccount"]:
        response: HTTPResponse = profile.http_session.get(
            constants.ENDPOINT__ACCOUNT__GET_ALL__CASH_ACCOUNT.replace("$profileId", str(profile.id)))
        return [CashAccount(
            id=data["id"],
            name=data["name"],
            currency=Currency(data["cashAmount"]["currency"]),
            balance=Decimal(str(data["cashAmount"]["value"])),
            profile=profile
        ) for data in response.data]

    @staticmethod
    def open(profile: Profile, currency: Currency) -> "CashAccount":
        account: Account = Account.abstract_open(profile, None, currency, False)
        cash_account: CashAccount = CashAccount.model_construct(**account.model_dump())
        cash_account.profile = profile

        profile.cash_account_list.append(cash_account)
        return cash_account


class ReserveAccount(Account):

    async def transfer(self, to_account: "CashAccount", amount: Decimal) -> "Transfer":
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if self.currency != to_account.currency:
            raise OperationNotSupportedException(
                "Direct inter-currency transfers from a reserve account is not supported")

        transfer: Transfer = Transfer.savings_to_cash_account_transfer(self.profile, self, to_account, amount)
        await DiscordDefaults.send_message(AortaTextChannels.WISE.value, f"**Intra-Account Transfer**:\n"
                                                                         f"*Timestamp*: {get_timestamp_string(datetime.datetime.now())}\n"
                                                                         f"*From*: {self.name}\n"
                                                                         f"*To*: {to_account.currency.value}\n"
                                                                         f"*Amount*: {self.currency.value} {'{:,}'.format(amount)}\n")

        self.profile.wise_account._initialize()
        return transfer

    @common.only_in_dev
    async def _simulate_top_up(self, amount: Decimal) -> None:
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cash_account: CashAccount = self.profile.get_cash_account(self.currency, True)
        cash_account._simulate_top_up(amount)
        await cash_account.transfer(self, amount)
        self.profile.wise_account._initialize()
        self.balance = (
            self.profile.wise_account.personal_profile.get_reserve_account(self.name, self.currency)).balance

    @common.only_in_dev
    async def _set_balance(self, amount: Decimal) -> None:
        if self.balance == amount:
            return
        elif self.balance < amount:
            await self._set_minimum_balance(amount)
        else:
            await self._set_maximum_balance(amount)

    @common.only_in_dev
    async def _set_minimum_balance(self, amount: Decimal) -> None:
        if self.balance >= amount:
            return

        amount_to_top_up: Decimal = amount - self.balance
        cash_account: CashAccount = self.profile.get_cash_account(self.currency, True)
        cash_account._simulate_top_up(amount_to_top_up)
        await cash_account.transfer(self, amount_to_top_up)

    @common.only_in_dev
    async def _set_maximum_balance(self, amount: Decimal) -> None:
        if self.balance <= amount:
            return

        maximum_transfer_amount: Decimal = Decimal(7_000_000)
        amount_to_deduct: Decimal = self.balance - amount
        cash_account: CashAccount = self.profile.get_cash_account(self.currency, True)
        hkd_account: CashAccount = self.profile.get_cash_account(common.Currency.HKD, True)
        await self.transfer(cash_account, amount_to_deduct)

        if amount_to_deduct > maximum_transfer_amount:
            await cash_account.transfer(hkd_account, maximum_transfer_amount)
            self._set_maximum_balance(amount)
        else:
            quote: Quote = Quote.get_quote(self.profile, cash_account, hkd_account, amount_to_deduct, True)
            await cash_account.transfer(hkd_account, quote.from_amount, is_amount_in_from_currency=True)

    @staticmethod
    def get_all(profile: Profile) -> List["ReserveAccount"]:
        response: HTTPResponse = profile.http_session.get(
            constants.ENDPOINT__ACCOUNT__GET_ALL__RESERVE_ACCOUNT.replace("$profileId", str(profile.id)))
        return [ReserveAccount(
            id=data["id"],
            name=data["name"],
            currency=Currency(data["cashAmount"]["currency"]),
            balance=Decimal(str(data["cashAmount"]["value"])),
            profile=profile,
        ) for data in response.data]

    @staticmethod
    def open(profile: Profile, account_name: str, currency: Currency) -> "ReserveAccount":
        account: Account = Account.abstract_open(profile, account_name, currency, True)
        reserve_account: ReserveAccount = ReserveAccount.model_construct(**account.model_dump())
        reserve_account.profile = profile

        profile.reserve_account_list.append(reserve_account)
        return reserve_account


class Recipient(DataClass):
    id: int
    account_holder_name: str
    currency: Currency
    is_self_owned: bool
    account_number: str
    profile: Profile
    _http_session: SyncHTTPSession = PrivateAttr()

    @staticmethod
    def get_all(profile: Profile) -> List["Recipient"]:
        response: HTTPResponse = profile.http_session.get(
            constants.ENDPOINT__RECIPIENT__GET_ALL.replace("$profileId", str(profile.id)))
        raw_recipient_list: List[Dict[str, Any]] = list(
            filter(lambda d: d["details"]["accountNumber"] is not None or d["details"]["iban"] is not None,
                   response.data))

        return [Recipient(
            id=data["id"],
            account_holder_name=data["accountHolderName"],
            currency=Currency(data["currency"]),
            is_self_owned=data["ownedByCustomer"],
            account_number=data["details"]["accountNumber"] if data["details"]["accountNumber"] is not None else data["details"]["iban"],
            profile=profile
        ) for data in raw_recipient_list]


class Quote(DataClass):
    id: str
    from_currency: Currency
    to_currency: Currency
    from_amount: Decimal
    to_amount: Decimal
    exchange_rate: Decimal
    profile: Profile

    @staticmethod
    def get_quote(profile: Profile, from_account: CashAccount | ReserveAccount,
                  to_account: CashAccount | ReserveAccount | Recipient, amount: Decimal,
                  is_amount_in_from_currency: bool = False) -> "Quote":
        response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__QUOTE__GET.replace("$profileId", str(profile.id)), data={
                "sourceCurrency": from_account.currency.value,
                "targetCurrency": to_account.currency.value,
                f"{'sourceAmount' if is_amount_in_from_currency else 'targetAmount'}": float(amount),
                "payOut": "BALANCE",
            })

        payment_option: Dict[str, Any] = next(
            filter(lambda p: p["payIn"] == "BALANCE", response.data["paymentOptions"]))
        return Quote(
            id=response.data["id"],
            from_currency=Currency(payment_option["sourceCurrency"]),
            to_currency=Currency(str(payment_option["targetCurrency"])),
            from_amount=Decimal(str(payment_option["sourceAmount"])),
            to_amount=Decimal(str(payment_option["targetAmount"])),
            exchange_rate=Decimal(str(response.data["rate"])),
            profile=profile
        )


class TransferType(Enum):
    CASH_TO_SAVINGS = auto()
    SAVINGS_TO_CASH = auto()
    CASH_TO_THIRD_PARTY = auto()
    SAVINGS_TO_THIRD_PARTY = auto()
    INTRA_CASH = auto()
    INTRA_SAVINGS = auto()


class Transfer(DataClass):
    id: int
    from_account: CashAccount | ReserveAccount
    to_account: CashAccount | ReserveAccount | Recipient
    from_amount: Decimal
    to_amount: Decimal
    reference: str | None
    transfer_type: TransferType | None

    @staticmethod
    def intra_cash_account_transfer(profile: Profile, from_account: CashAccount, to_account: CashAccount,
                                    amount: Decimal, is_amount_in_from_currency: bool = False) -> "Transfer":
        quote: Quote = Quote.get_quote(profile, from_account, to_account, amount, is_amount_in_from_currency)
        response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__BALANCE__MOVE_MONEY_BETWEEN_BALANCES.replace("$profileId", str(profile.id)),
            data={"quoteId": quote.id},
            headers={"X-idempotence-uuid": str(uuid.uuid4())})

        return Transfer(
            id=response.data["id"],
            from_account=from_account,
            from_amount=Decimal(str(response.data["sourceAmount"]["value"])),
            to_account=to_account,
            to_amount=Decimal(str(response.data["targetAmount"]["value"])),
            reference=None,
            transfer_type=TransferType.INTRA_CASH,
        )

    @staticmethod
    def cash_to_savings_account_transfer(profile: Profile, from_account: CashAccount, to_account: ReserveAccount,
                                         amount: Decimal) -> "Transfer":
        data = {
            "sourceBalanceId": from_account.id,
            "targetBalanceId": to_account.id
        }

        if from_account.currency != to_account.currency:
            quote: Quote = Quote.get_quote(profile, from_account, to_account, amount)
            data["quoteId"] = cast(int, quote.id)
        else:
            data["amount"] = {  # type: ignore[assignment]
                "value": float(amount),
                "currency": to_account.currency.value
            }

        response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__BALANCE__MOVE_MONEY_BETWEEN_BALANCES.replace("$profileId", str(profile.id)), data=data,
            headers={"X-idempotence-uuid": str(uuid.uuid4())})

        return Transfer(
            id=response.data["id"],
            from_account=from_account,
            from_amount=Decimal(str(response.data["sourceAmount"]["value"])),
            to_account=to_account,
            to_amount=Decimal(str(response.data["targetAmount"]["value"])),
            reference=None,
            transfer_type=TransferType.CASH_TO_SAVINGS,
        )

    @staticmethod
    def cash_to_third_party_cash_account_transfer(profile: Profile, from_account: CashAccount, to_account: Recipient,
                                                  amount: Decimal, reference: str | None = None,
                                                  is_amount_in_from_currency: bool = False) -> "Transfer":
        quote: Quote = Quote.get_quote(profile, from_account, to_account, amount, is_amount_in_from_currency)
        data: Dict[str, Any] = {
            "targetAccount": to_account.id,
            "quoteUuid": quote.id,
            "customerTransactionId": str(uuid.uuid4()),
            "details": {
                "reference": "" if reference is None else reference,
            }
        }

        create_transfer_response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__TRANSFER__CREATE_THIRD_PARTY_TRANSFER, data=data)
        profile.http_session.post(
            constants.ENDPOINT__TRANSFER__FUND_THIRD_PARTY_TRANSFER.replace("$profileId", str(profile.id)).replace(
                "$transferId", str(create_transfer_response.data["id"])),
            data={"type": "BALANCE"})

        return Transfer(
            id=create_transfer_response.data["id"],
            from_account=from_account,
            from_amount=Decimal(str(create_transfer_response.data["sourceValue"])),
            to_account=to_account,
            to_amount=Decimal(str(create_transfer_response.data["targetValue"])),
            reference=None,
            transfer_type=TransferType.CASH_TO_THIRD_PARTY,
        )

    @staticmethod
    def savings_to_cash_account_transfer(profile: Profile, from_account: ReserveAccount, to_account: CashAccount,
                                         amount: Decimal) -> "Transfer":
        data = {
            "amount": {
                "value": float(amount),
                "currency": from_account.currency.value
            },
            "sourceBalanceId": from_account.id,
            "targetBalanceId": to_account.id,
        }

        response: HTTPResponse = profile.http_session.post(
            constants.ENDPOINT__BALANCE__MOVE_MONEY_BETWEEN_BALANCES.replace("$profileId", str(profile.id)), data=data,
            headers={"X-idempotence-uuid": str(uuid.uuid4())})

        return Transfer(
            id=response.data["id"],
            from_account=from_account,
            from_amount=Decimal(str(response.data["sourceAmount"]["value"])),
            to_account=to_account,
            to_amount=Decimal(str(response.data["targetAmount"]["value"])),
            reference=None,
            transfer_type=TransferType.SAVINGS_TO_CASH,
        )


class DebitCard(DataClass):
    profile: Profile
    token: str
    expiry_date: datetime.datetime
    bank_identification_number: str

    # TODO: Find out why this endpoint returns a 403 (Unauthorized)
    @staticmethod
    def get_all(profile: Profile) -> List["DebitCard"]:
        response: HTTPResponse = profile.http_session.get(constants.ENDPOINT__DEBIT_CARD__GET_ALL.replace("$profileId", str(profile.id)))
        return [DebitCard(
            profile=profile,
            token=data["token"],
            expiry_date=datetime.datetime.fromisoformat(data["expiryDate"]),
            bank_identification_number=data["bankIdentificationNumber"]
        ) for data in response.data["cards"]]


class AccountDebit(DataClass):
    wise_id: int
    is_attempted: bool
    is_successful: bool
    timestamp: datetime.datetime
    transaction: Transaction | None = None

    @staticmethod
    def get_from_request_data(request_data: Dict[str, Any], wise_account: WiseAccount) -> "AccountDebit":
        personal_profile: PersonalProfile = wise_account.personal_profile
        id: int = request_data["data"]["resource"]["id"]
        cash_account: CashAccount
        transaction: Transaction

        for ca in personal_profile.cash_account_list:
            try:
                transaction = next(filter(lambda t: id == t.id, ca.get_transactions()))
                cash_account = cast(CashAccount, transaction.account)
                break
            except StopIteration:
                continue

        return AccountDebit(wise_id=request_data["data"]["resource"]["id"],
                            is_attempted=request_data["data"]["current_state"] == "incoming_payment_waiting",
                            is_successful=request_data["data"]["current_state"] == "outgoing_payment_sent",
                            timestamp=request_data["data"]["occurred_at"],
                            transaction=transaction)


class AccountCredit(DataClass):
    wise_id: int
    account: CashAccount
    transaction: Transaction | None
    account_balance: Decimal
    timestamp: datetime.datetime

    @staticmethod
    def get_from_request_data(request_data: Dict[str, Any], wise_account: WiseAccount) -> "AccountCredit":
        personal_profile: PersonalProfile = wise_account.personal_profile
        cash_account: CashAccount = personal_profile.get_cash_account(Currency(request_data["data"]["currency"]))
        timestamp: datetime.datetime = common.get_timestamp_from_string(request_data["data"]["occurred_at"], "UTC")

        try:
            transaction: Transaction | None = next(filter(lambda t: int(t.timestamp.timestamp()) == int(timestamp.timestamp()), cash_account.get_transactions()))
        except StopIteration:
            transaction = None

        return AccountCredit(wise_id=request_data["data"]["resource"]["id"],
                             account=cash_account,
                             transaction=transaction,
                             account_balance=Decimal(request_data["data"]["post_transaction_balance_amount"]),
                             timestamp=request_data["data"]["occurred_at"])


class WiseWebhook:

    @classmethod
    def get_balance_update_object(cls, request_data: Dict[str, Any],
                                  wise_account: WiseAccount) -> AccountDebit | AccountCredit | None:
        if request_data["event_type"] == "transfers#state-change":
            return AccountDebit.get_from_request_data(request_data, wise_account)
        elif request_data["event_type"] == "balances#credit":
            return AccountCredit.get_from_request_data(request_data, wise_account)

        return None


WiseAccount.model_rebuild()
Profile.model_rebuild()
PersonalProfile.model_rebuild()
BusinessProfile.model_rebuild()
Account.model_rebuild()
DebitCard.model_rebuild()
Transaction.model_rebuild()
AccountDebit.model_rebuild()
AccountCredit.model_rebuild()
