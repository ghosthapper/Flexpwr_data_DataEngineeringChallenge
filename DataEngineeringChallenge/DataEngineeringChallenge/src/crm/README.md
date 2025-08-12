# Contractual data

Each asset is assigned to a contract with a customer.\ 
For simplification in this challenge we will assume that a contract can only be assigned to one asset and that a 
customer can sign only one contract with FlexPower
Contractual data determines how assets are to be invoiced and is kept in the CRM.

The data is a csv and contains the following attributes:

- contract_id: a unique alphanumerical identifier for the contract.
- asset_id: a unique alphanumerical identifier for the asset.
- metering_point_id: a unique alphanumerical identifier for the asset's metering point.
- capacity: the installed capacity of the asset, in MW.
- technology: the technology used by the asset, can be either "solar" or "wind".
- contract_begin: the date when the asset's contract with FlexPower began.
- contract_end: the date when the asset's contract with FlexPower ends, can be none.
- price_model: the pricing model used by the asset, can be either "fixed" or "market".
- price: the price paid by FlexPower to the asset owner, in €/MWh, if asset in the "fixed" price model.
- fee_model: the fee model used by the asset, can be either "fixed_as_produced", "fixed_for_capacity", or "percent_of_market".
- fee: the fee paid by the asset owner to FlexPower, in €/MWh, if asset in the "fixed" fee model.
- fee_percent: percentage of the market value paid by the asset owner to FlexPower per MWh, in %, if asset in the
  "percent_of_market" fee model.
- email: email of the customer on which we send the invoice

A new file is created every week, on Sunday, between 04:30 and 05:00.
The portfolio operations team might create new files on demand if some urgent changes need to be ingested.