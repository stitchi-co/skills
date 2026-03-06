# Pipeline Reference

## Projects Pipeline (id=3)
Individual orders and projects. Lumpy, transactional revenue. Each deal = one customer request.

| Stage | ID | Probability | Description |
|-------|-----|-------------|-------------|
| Scheduled | 55 | 40% | Future known work (calendar items, tentative) |
| Request | 48 | 60% | Actively scoping requirements |
| Quoted | 25 | 70% | Proposal sent, awaiting approval |
| Approved | 23 | 90% | PO received, ready for production |
| In Production | 56 | 95% | With vendors/warehouse |

Won = delivered. Flow: Scheduled → Request → Quoted → Approved → In Production → Won.

## New Business Pipeline (id=9)
Measures annual expected value of new logos. Deal value = estimated annual account value, not a single order.

| Stage | ID | Probability | Description |
|-------|-----|-------------|-------------|
| Discovery | 59 | 25% | Understanding merch program needs |
| Proposal | 60 | 50% | Presenting capabilities + first project |
| Negotiation | 61 | 75% | Terms, pricing, timeline |

A New Business deal is considered **won** when the account has at least one won project in the Projects pipeline. The New Business deal represents the relationship/account value, not a transaction.

## Account Tiers (Custom Field 54)
Annual expected value buckets for new logos:

| Tier | ID | Annual Value | Typical Profile |
|------|-----|-------------|-----------------|
| XS | 246 | ~$5K | Small biz, 1-2 orders/year |
| S | 247 | ~$20K | Growing company, quarterly orders |
| M | 248 | ~$50K | Mid-market, regular program |
| L | 249 | ~$125K | Large org, multiple use cases |
| XL | 250 | ~$250K+ | Enterprise, full merch program |

## Key Custom Fields

Pipedrive stores custom fields with hashed keys in the API. Mapping:

| Field | ID | API Key | Options |
|-------|-----|---------|---------|
| Account Tier | 54 | `f331c0d704a785facd6d48b0af3cf1a08ff2b55c` | 246=XS, 247=S, 248=M, 249=L, 250=XL |
| Opportunity Type | 55 | `7568cd7dc2b8dfa1900802ebae3b4950f461075b` | 251=New Account, 252=New Program, 253=Expansion |
| In-Hands Date | 50 | `4f370fd7ef57ae614f7aece2d3eb06fa4def8463` | date |
| Source Campaign | 53 | `7ddcc3c39b35eea5ed08af59e2dfe3ff89ef9a52` | enum |
| Is First Order? | 52 | *(lookup if needed)* | 190=Yes, 191=No |

## The Two Pipeline Stories

**Projects** tells you about *execution and revenue flow*:
- Are we winning the work customers bring us?
- Is production on track?
- Where are bottlenecks (quoting? approval? production)?
- Revenue is lumpy — look at trends, not single weeks.

**New Business** tells you about *growth and future health*:
- Are we building relationships with the right-sized accounts?
- Are prospects moving through stages or stalling?
- Is our bucket distribution healthy (enough M/L/XL vs. all XS)?
- Stage velocity matters more than raw count.
