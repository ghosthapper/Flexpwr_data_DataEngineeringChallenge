# Invoicing

At the end of each month, FlexPower invoices the asset owners based on the production of their assets:
FlexPower pays the asset owner an agreed-upon price for each produced MWh, and the asset owner pays FlexPower
a fee for the services provided, per MWh. \
There are different pricing and fee models, i.e., ways to compute the price and fee, to accommodate different
types of assets and customers.\

In the invoices we send out to the customers, we need to compute the following entries:

- **infeed payout**: multiplying the production of the asset by the price we agreed upon with the asset owner,
  depending on the price model.
  For the **fixed** pricing model, we just multiply the total produced volume with the price from the base data.
  This is a more "conservative" pricing model.
  For the **market** pricing model, we multiply the production of the asset, for each quarter-hour, with the market
  VWAP (VWAP computed with public trades).
  This is a price model that is more sensitive to the market price fluctuations and can yield a better payout if the
  asset is producing at times when the price on the market is high.
- **fees**: multiplying the production of the asset by the fee we agreed upon with the asset owner, depending on the fee
  model.
  For the **fixed_as_produced** fee model, we multiply the total produced volume with the fee from the base data.
  For the **fixed_for_capacity** fee model, we multiply the installed capacity of the asset with the fee from the base
  data.
  For the **percent_of_market** fee model, we multiply the total produced volume of the asset with the market VWAP and
  the fee percent from the base data.
  For each of these entries we also compute the unitary net amount, the VAT (at a rate of 19%) and the total gross
  amount.
- **redispatch payout**: We have to compensate customers for the redispatched volumes,
  as it was not "their fault" that their asset was turned off.
  The compensation is calculated by multiplying the latest forecasted volume for the redispatched asset with the
  compensation price provided by the DSO. Later on, FlexPower would claim this amount from the DSO by sending them
  an invoice.

An invoice is identified with the invoicing month, the corresponding contract id. \
As some data involved in calculating the invoice could evolve over time, there is also a notion of versioning
for invoices. For the sake of this challenge, we will assume that the data we have when we compute the invoice is 
final and binding and there is only one version for each invoice.