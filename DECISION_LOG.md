# Skylark Drones BI Agent — Decision Log

## 1. Objective

Build a conversational Business Intelligence agent that allows founders
and executives to ask questions about Deals and Work Orders stored in
Monday.com.

The agent dynamically retrieves data from Monday.com rather than
hardcoding the supplied CSV data.

## 2. Architecture and Technology Choices

### Python

Python was selected because it provides strong support for data
processing, API integration, and rapid prototyping within the six-hour
assignment constraint.

### Pandas

Pandas is used for data transformation, cleaning, aggregation, and
business analytics.

### Streamlit

Streamlit was selected for the conversational web interface because
it allows the prototype to be hosted quickly without requiring a
separate frontend application.

### Monday.com API

The Monday.com API is used as the runtime source of truth. The agent
retrieves Deals and Work Orders dynamically from their respective
Monday.com boards.

## 3. Key Assumptions

- Monday.com is treated as the source of truth for current business data.
- When a query refers to "this quarter" without specifying a fiscal
  calendar, calendar-quarter interpretation is used.
- Missing numerical values are not automatically treated as meaningful
  business values.
- Missing dates are explicitly identified rather than silently inferred.
- Deal Stage is treated as the primary indicator of sales-funnel position.
- Different status fields are preserved because they represent
  different operational dimensions.
- When the available data is insufficient to answer a question reliably,
  the agent reports the limitation instead of inventing a value.

## 4. Data Resilience

The supplied data contains several real-world quality issues, including:

- Missing values
- Missing deal close dates
- Inconsistent status values
- Mixed quantity formats such as numbers combined with units
- Inconsistent sector/service labels
- Blank financial fields
- Duplicate or embedded header information
- Different representations of product combinations

The implementation attempts to normalize these values and exposes
data-quality limitations in responses.

This prevents incomplete business records from being presented as
fully reliable information.

## 5. Query Understanding

The agent supports founder-level questions covering:

- Pipeline health
- Sector performance
- Deal stages
- Deal values
- Work-order execution
- Billing
- Collections
- Receivables
- Data quality
- Cross-board customer analysis
- Leadership summaries

Ambiguous queries are handled using documented assumptions where a
reasonable interpretation is possible.

## 6. Cross-Board Analysis

Deals and Work Orders are stored separately in Monday.com.

For questions requiring information from both datasets, the system
retrieves both boards and performs analysis using common business
identifiers such as customer/client information where available.

This enables questions such as identifying customers that have both
open deals and outstanding receivables.

## 7. Leadership Updates

The optional leadership-update requirement was interpreted as a
concise executive summary.

The leadership update focuses on:

- Pipeline position
- Revenue and financial indicators
- Work-order/operations status
- Receivables and collections
- Data-quality concerns
- Key business risks and areas requiring attention

The objective is to provide decision-oriented information rather than
simply displaying raw database values.

## 8. Trade-offs

Given the six-hour implementation constraint, the solution prioritizes:

- Working end-to-end integration
- Reliable Monday.com retrieval
- Business-focused analytics
- Data-quality awareness
- Simple deployment
- Easy demonstration

A more advanced production system could add a dedicated backend,
database/cache layer, stronger semantic query planning, authentication,
automated monitoring, and more sophisticated LLM-based tool selection.

## 9. What I Would Improve With More Time

With additional development time, I would add:

1. More sophisticated natural-language query understanding.
2. Stronger automated data-quality validation.
3. Caching to reduce repeated Monday.com API calls.
4. More advanced cross-board entity matching.
5. Role-based access control.
6. Automated scheduled leadership reports.
7. Unit tests and integration tests.
8. Monitoring and API-failure alerting.
9. More detailed visual dashboards.
10. Production-grade logging and observability.
