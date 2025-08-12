# DataEngineeringChallenge @ CFP FlexPower

<div style="display: flex; justify-content: center;">
  <img src="img.png" alt="FlexPower">
</div>



## Background

At FlexPower, engineers:
- design, build and run reliable serverless systems.
- collaborate closely with traders, sales and operations to build internal tools that help the company get the best outcomes
  on the markets, thus making renewables more profitable.
- work with market and asset data to generate insights and data-driven trading decisions.

This challenge is meant to give you a taste of the type of problems our engineering team has to solve with regard to
data. It should help you decide if you might have fun working with us.\
It is also an opportunity to demonstrate your technical skills and the ability to understand and work with our domain.

## Intro

One of FlexPower's main products is the so-called **[RouteToMarket](https://flex-power.energy/services/renewables-trading/)**: 
bringing the energy produced by renewable assets to the European electricity markets.

FlexPower signs contracts with renewable asset owners, and then sells the energy produced by
these assets on the electricity market, hopefully profitably thanks to its trading expertise.\
FlexPower has to monitor the performance of its trading activities while the trading is happening, so that
the trading desk can make informed data-driven decisions.

In this challenge, we will look at different aspects of marketing renewables and present different data
entities involved.\
The goal will be to compute different financial flows and present them in a way that helps stakeholders
understand the performance of the portfolio and of single assets.

**PS:** FlexPower also provides supply customers with energy (so assets consuming energy, for example, EV charging
stations). The structure is essentially the same, but for simplicity's sake we will consider only production 
in this challenge.

## The challenge

Your goal is to help FlexPower make sense of all this data and perform some key functions of the business.\
As a general instruction, data needs to be ingested and persisted so that we can compute relevant
quantities and display them to the different users and teams. 
You can adopt any adequate "frontend" solution, from graph captures to jupyter notebooks and dash or grafana web app.\
Most data is coming from files that are distributed within directories, but this is rather a simplification.
In practice, data would come from APIs, SFTP servers, S3 buckets... Also, this challenge doesn't account for any form 
of authentication or rate limitation that we might face in practice.

In particular, the dataset is centered around the delivery day 2025-06-08. Here are the individual tasks you can work on:

- **Task 1: Asset and Portfolio Forecasting** - Compute the latest forecast for each asset and then the latest forecast for the whole portfolio.

- **Task 2: Best-of-Infeed Analysis** - Compute best-of-infeed on the asset level and then as an aggregation for the whole portfolio.

- **Task 3: Trading Performance Metrics** - Compute the trading revenues, number of trades, net traded volume and VWAP.

- **Task 4: Imbalance Cost Analysis** - Compute the imbalance cost for each asset and for the total portfolio.

- **Task 5: Invoice Generation** - Compute invoices for each asset.

- **Task 6: Performance Reporting** - Create a report that helps FlexPower understand the performance of its portfolio and each single asset.

- **Task 7: Data Permissions Framework** - Think about a permissions concept for data and reports.

**Important**: **We do NOT expect you to complete all tasks!** Feel free to focus on a subset of tasks that deliver 
some value or some of the business features that we mention.\
Whether you enjoy building data integrations or diving into analytics engineering, go with what excites you. 
Quality over quantity is what we're looking for.

You are also welcome to explore aspects not covered in these tasks or combine elements from different tasks.
The deliverable is intentionally flexible to give you freedom to explore, but if you need more specific guidance,
we can provide more detailed approaches to tackle any particular task. Please reach out to us and ask for some help.

## Data Overview

### Assets "base" data
With base data we usually mean static attributes of assets. These can be **technical** or **contractual**.
We call all assets traded by FlexPower the **portfolio**.

- **Technical data**: Asset specifications and properties → [Virtual Power Plant Documentation](src/vpp/README.md)
- **Contractual data**: Contract details and pricing models → [Customer Relationship Management Documentation](src/crm/README.md)

### Production Data
Given how the RouteToMarket product functions, infeed data plays a central role in our system.

- **Forecasts & Live measurements**: Production forecasts and real-time data → [Virtual Power Plant Documentation](src/vpp/README.md)
- **Final measurements & Redispatch**: Official production data and grid interventions → [Distribution System Operator Documentation](src/distribution_system_operator/README.md)

### Trading Data
Energy trading data from exchanges and internal trading activities.

- **Private & Public trades, VWAPs**: Trading execution and market data → [Exchange Documentation](src/exchange/README.md)

### Financial Data

- **Invoicing**: Customer billing processes and calculations → [Invoicing Documentation](src/invoicing/invoicing.md)

- **Imbalance**: Grid balancing penalties and costs → [Imbalance Documentation](src/imbalance/README.md)


## Submission Instructions

- Create a GitHub repository containing your solution and provide us with access so that we can review your code.
- Make sure to add all the necessary instructions to run the solution within the readme.
- Feel free to add any notes about technology choices and design decisions, as well as anything that we should keep in
  mind when reviewing your code. The challenge provides a lot of details
- AI is part of the developer tools now, so there is no problem leveraging it to help you solve the problem.
  If you do use AI, please provide us with a quick description of what tools you use and how you used them to work
  through the challenge.

## Notes

- Spend as much time as you want on the challenge to produce something you are proud of.
- The challenge is extensive, and you don't have to do everything, prefer quality to quantity. Feel free to make
  approximations (we do as well).
- You can use any tools you want, but we recommend using Python for any coding involved and SQL for queries and data
  processing.
- The solution is important, but so is everything else around it: unit tests, commit size and description, README and
  instructions to use the solution...
- If you already have similar personal projects that you would like to submit instead of this one, it's also possible.
  Just make sure that you include exhaustive documentation on what it's about, how we can run it and how it is relevant
  or similar to our challenge.

## A small comment on units
- volumes can be in megawatt (or MW, i.e. power) or megawatt-hour (or MWh, i.e. energy)
- converting from MW to MWh depends on the delivery range: if the delivery range is hourly, then the multiplication factor is 1, otherwise it is quarter-hourly, then the multiplication factor is 0.25, i.e.
```python
volume_mwh = volume_mw * 0.25
```
