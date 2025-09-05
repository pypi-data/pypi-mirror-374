from dataclasses import dataclass
from typing import List
from exsited.exsited.account.dto.account_nested_dto import *
from exsited.exsited.common.dto.common_dto import *
from exsited.exsited.order.dto.order_dto import OrderDataDTO
from exsited.exsited.order.dto.order_nested_dto import OrderPropertiesDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class PricingRuleDTO(ABBaseDTO):
    price: str = None


@dataclass(kw_only=True)
class ItemPriceSnapshotDTO(ABBaseDTO):
    pricingRule: PricingRuleDTO = None


@dataclass(kw_only=True)
class ItemPriceTaxDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: float = None


@dataclass(kw_only=True)
class PaymentAppliedDTO(ABBaseDTO):
    processor: str = None
    amount: str = None


@dataclass(kw_only=True)
class PaymentDTO(ABBaseDTO):
    paymentApplied: List[PaymentAppliedDTO] = None


@dataclass(kw_only=True)
class InvoiceDTO(ABBaseDTO):
    payment: PaymentDTO = None


@dataclass(kw_only=True)
class ContractPropertiesDTO(ABBaseDTO):
    requireCustomerAcceptance: str = None
    requiresPaymentMethod: str = None
    initialContractTerm: str = None
    renewAutomatically: str = None
    autoRenewalTerm: str = None
    allowEarlyTermination: str = None
    applyEarlyTerminationCharge: str = None
    allowPostponement: str = None
    maximumDurationPerPostponement: str = None
    maximumPostponementCount: str = None
    allowTrial: str = None
    startContractAfterTrialEnds: str = None
    trialPeriod: str = None
    allowDowngrade: str = None
    periodBeforeDowngrade: str = None
    allowDowngradeCharge: str = None
    downgradeChargeType: str = None
    downgradeChargeFixed: str = None
    allowUpgrade: str = None


@dataclass(kw_only=True)
class OrderLineDTO(ABBaseDTO):
    itemId: str = None
    itemOrderQuantity: int = None
    itemPriceSnapshot: ItemPriceSnapshotDTO = None
    itemPriceTax: ItemPriceTaxDTO = None
    packageName: str = None


@dataclass(kw_only=True)
class OrderDTO(ABBaseDTO):
    lines: List[OrderLineDTO] = None
    invoice: InvoiceDTO = None
    allowContract: str = None
    contractProperties: ContractPropertiesDTO = None
    properties: OrderPropertiesDTO = None


@dataclass(kw_only=True)
class AccountDTO(ABBaseDTO):
    name: str = None
    emailAddress: str = None
    status: str = None
    id: str = None
    displayName: str = None
    description: str = None
    invoiceParentAccount: str = None
    type: str = None
    imageUri: str = None
    grantPortalAccess: str = None
    website: str = None
    linkedin: str = None
    twitter: str = None
    facebook: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    parentAccount: str = None
    group: str = None
    manager: str = None
    referralTracking: str = None
    salesRep: str = None
    pricingLevel: PricingLevelDTO = None

    currency: CurrencyDTO = None
    timeZone: TimeZoneDTO = None
    tax: TaxDTO = None
    accountingCode: AccountingCodeDTO = None
    communicationPreference: list[CommunicationPreferenceDTO] = None
    paymentMethods: list[PaymentMethodsDataDTO] = None
    billingPreferences: BillingPreferencesDTO = None
    customAttributes: list[CustomAttributesDTO] = None
    try:
        addresses: list[AcccountAddressDTO] = None
        contacts: list[ContactDTO] = None
    except:
        addresses: list[AcccountAddressRequestDTO] = None
        contacts: list[ContactRequestDTO] = None
    customForms: CustomFormsDTO = None
    eventUuid: str = None
    customObjects: list[CustomObjectDTO] = None
    kpis: dict = None
    id: str = None
    try:
        order: OrderDTO = None
    except:
        order: OrderDataDTO = None


@dataclass(kw_only=True)
class ExpressDTO(ABBaseDTO):
    account: AccountDTO = None
    _custom_field_mapping = {
        "isTaxExemptWhenSold": "isTaxExemptWhenSold"
    }