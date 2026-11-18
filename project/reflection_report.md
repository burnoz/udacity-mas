# Reflection

## System Architecture

Due to the project specifications, this MAS follows an Orchestrator pattern. After reading through the requirements and defining the system's core responsibilities, I decided to implement the following agents:

- OrchestratorAgent: handles customes requests and delegates tasks to the worker agents to compile a final response to the customer.
- InventoryAgent: checks the warehouse inventory and supplier delivery dates to determine if requested items can be fulfilled by the customer's deadline.
- QuotingAgent: generates itemized quotes with tiered bulk discounts based on historical quote data and current inventory status.
- TransactionAgent: processes financial transactions, including supplier restocks and customer sales, and generates financial reports.

The system was built with the following flow in mind:

1. Customer Inquiry Input: Incoming text-based customer requests (along with the request date and requested delivery deadline) are received by the Orchestrator Agent.
2. Step 1 - Inventory & Delivery Verification (InventoryAgent): The Orchestrator delegates stock verification and supplier delivery timeline estimation to the Inventory Agent, which queries the SQLite database using get_all_inventory, get_stock_level and get_supplier_delivery_date.
3. Step 2 - Quote Generation & Bulk Discounting (QuotingAgent): Using the verified inventory status, the Orchestrator delegates pricing to the Quoting Agent, which searches historical quotes via search_quote_history and computes itemized pricing with strategic tiered bulk discounts.
4. Step 3 - Order Fulfillment & Financial Reporting (TransactionAgent): For all fulfillable items that meet the customer's delivery deadline, the Orchestrator instructs the Transaction Agent to check cash reserves (get_cash_balance), execute necessary supplier restock (stock_orders) and customer sale (sales) transactions (create_transaction) and produce an updated financial health snapshot (generate_financial_report).
5. Step 4 - Customer Response Synthesis (OrchestratorAgent): Finally, the Orchestrator synthesizes the outputs from all three worker agents into a clear, transparent customer response detailing fulfilled items, itemized prices and bulk discounts applied, delivery dates and explicit explanations for any unfulfilled or rejected items.

The tools were creted by wrapping the provided functions in the starting project template:
- get_all_inventory(as_of_date) -> check_all_inventory
- get_stock_level(item_name, as_of_date) -> check_item_stock & record_order_transaction
- get_supplier_delivery_date(input_date_str, quantity) -> check_supplier_delivery, check_item_stock, & record_order_transaction
- search_quote_history(search_terms, limit) -> get_quote_history
- create_transaction(item_name, transaction_type, quantity, price, date) -> record_order_transaction
- get_cash_balance(as_of_date) -> check_company_cash & record_order_transaction
- generate_financial_report(as_of_date) -> get_company_financial_report

![System Workflow](workflow_diagram.png)

## Evaluation Results

### Quantitative Summary

The multi-agent system was evaluated against all 20 simulated customer requests in quote_requests_sample.csv spanning **April 1, 2025 to April 17, 2025**:

| Metric | Initial State (`2025-04-01`) | Final State (`2025-04-17`) | Net Change / Outcome |
| :--- | :--- | :--- | :--- |
| **Cash Balance** | `\$45,059.70` | `\$45,210.65` | **`+\$150.95`** |
| **Warehouse Inventory Value** | `\$4,940.30` | `\$4,263.90` | `-\$676.40` (initial stock sold into cash) |
| **Total Requests Processed** | — | `20` | `100%` completion rate (`test_results.csv`) |
| **Orders Fulfilled (Full or Partial)** | — | **`17 orders`** (5 full, 12 partial) | Exceeds rubric minimum ($\ge 3$ fulfilled) |
| **Orders Completely Rejected** | — | **`3 orders`** (Requests #13, #15, #18) | Exceeds rubric minimum ($\ge 1$ rejected) |
| **Orders with Partial Item Rejections** | — | **`12 orders`** (Requests #1, #2, #3, #4, #5, #9, #11, #14, #16, #17, #19, #20) | Non-catalog items or item-level stock/deadline constraints rejected cleanly |

---

### Detailed Request-by-Request Evaluation Breakdown

| Req ID | Request Date | Event & Job Context | Outcome | Cash Balance After (`\$`) | Inventory Value After (`\$`) | Key System Behavior & Notes |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `2025-04-01` | Ceremony (Office Manager) | **Partial Fulfillment** | `45,107.20` | `4,890.30` | Fulfilled 100 Colored paper (`\$9.50`, 5% off) + 200 Glossy paper (`\$38.00`, 5% off) (`\$47.50`); rejected 100 heavy cardstock (0 stock). |
| **2** | `2025-04-03` | Parade (Hotel Manager) | **Partial Fulfillment** | `45,093.95` | `4,890.30` | Fulfilled 300 Party streamers (`\$14.25`) + 500 Poster paper (`\$112.50`) (`\$126.75`); rejected non-catalog `"balloons"`. |
| **3** | `2025-04-04` | Conference (School Board) | **Partial Fulfillment** | `45,023.80` | `4,883.45` | Fulfilled 10,000 A4 paper (15% off, `\$425.00`) + 500 Standard copy paper (10% off, `\$18.00`) (`\$443.00`); rejected non-catalog `"A3 paper"`. |
| **4** | `2025-04-05` | Reception (Non-Profit Dir.) | **Partial Fulfillment** | `45,068.35` | `4,831.40` | Fulfilled 500 Recycled cardstock (10% off, `\$67.50`); rejected 250 A4 printer paper due to insufficient stock. |
| **5** | `2025-04-05` | Party (School Teacher) | **Partial Fulfillment** | `45,126.10` | `4,766.40` | Fulfilled 500 Colored paper (`\$45.00`) + 300 Cardstock (`\$42.75`) (`\$87.75`); rejected 200 Washi tape (0 stock). |
| **6** | `2025-04-06` | Assembly (Event Planner) | **Full Fulfillment** | `45,120.50` | `4,766.40` | Fulfilled 300 Standard copy paper (`\$11.40`) + 500 Construction paper (`\$31.50`) + 200 Cardstock (`\$28.50`) (`\$71.40`). |
| **7** | `2025-04-07` | Exhibition (Art Director) | **Full Fulfillment** | `45,413.50` | `4,418.40` | Fulfilled 200 250 gsm cardstock (`\$57.00`) + 1,000 Matte paper (`\$153.00`) + 500 Glossy paper (`\$90.00`) + 300 Large poster paper (`\$285.00`) (`\$585.00`). |
| **8** | `2025-04-07` | Fair (Event Organizer) | **Full Fulfillment** | `45,315.00` | `4,413.90` | Fulfilled 500 Glossy (`\$90.00`) + 1,000 Matte (`\$153.00`) + 2,000 Colored (`\$170.00`) + 3,000 Recycled paper (`\$204.00`) (`\$617.00`). |
| **9** | `2025-04-07` | Campaign (Marketing Mgr.) | **Partial Fulfillment** | `45,294.00` | `4,433.90` | Fulfilled 100 Glossy paper (`\$19.00`) + 50 Envelopes (`\$2.50`) (`\$21.50`); rejected 200 A4 paper (restock arrives after `2025-04-10` deadline). |
| **13** | `2025-04-08` | Performance (Receptionist) | **Rejected** | `45,294.00` | `4,433.90` | **Complete Rejection**: 500 A4 paper and 200 Cardstock supplier restock arrives `2025-04-12`, after the `2025-04-10` deadline. |
| **12** | `2025-04-08` | Carnival (Volunteer) | **Full Fulfillment** | `45,290.40` | `4,433.90` | Fulfilled 100 Paper napkins (`\$1.90`) + 200 Cardstock (`\$28.50`) + 500 Standard copy paper (`\$18.00`) (`\$48.40`). |
| **10** | `2025-04-08` | Show (Restaurant Owner) | **Full Fulfillment** | `45,298.15` | `4,413.90` | Fulfilled 500 Glossy paper (10% off, `\$90.00`) + 300 Cardstock (5% off, `\$42.75`) (`\$132.75`). |
| **11** | `2025-04-08` | Demonstration (Coordinator) | **Partial Fulfillment** | `45,288.15` | `4,413.90` | Fulfilled 500 Glossy paper (10% off, `\$90.00`); rejected 300 Matte paper due to 0 warehouse stock. |
| **14** | `2025-04-09` | Gala (PR Manager) | **Partial Fulfillment** | `45,280.65` | `4,413.90` | Fulfilled 500 Cardstock (`\$67.50`); rejected 5,000 A4 paper and 2,000 Poster paper (restock arrives after `2025-04-15` deadline). |
| **15** | `2025-04-12` | Rally (Creative Director) | **Rejected** | `45,280.65` | `4,413.90` | **Complete Rejection**: 10,000 A4 paper (`2025-04-19`), 5,000 Colored paper (`2025-04-19`), and 500 Heavyweight paper (`2025-04-16`) miss the `2025-04-15` deadline. |
| **16** | `2025-04-13` | Festival (Event Manager) | **Partial Fulfillment** | `45,375.65` | `4,313.90` | Fulfilled 100 Large poster paper (5% off, `\$95.00`); rejected 200 Construction paper and 500 A4 paper (restock misses `2025-04-15` deadline). |
| **17** | `2025-04-14` | Reception (Admin Asst.) | **Partial Fulfillment** | `45,420.65` | `4,263.90` | Fulfilled 500 Paper plates (10% off, `\$45.00`); rejected Paper cups, Paper napkins, Colored paper, and A4 paper due to stock/deadline constraints. |
| **18** | `2025-04-14` | Ceremony (Office Manager) | **Rejected** | `45,420.65` | `4,263.90` | **Complete Rejection**: 500 Cardstock, 1,000 Standard copy paper, and 200 Colored paper restocks arrive `2025-04-18`, after the `2025-04-15` deadline. |
| **19** | `2025-04-15` | Exhibition (City Hall Clerk) | **Partial Fulfillment** | `45,398.15` | `4,263.90` | Fulfilled 1,000 Cardstock (15% off, `\$127.50`); rejected 2,000 Glossy paper and 500 Matte paper (restock misses `2025-04-20` deadline). |
| **20** | `2025-04-17` | Concert (Restaurant Mgr.) | **Partial Fulfillment** | `45,210.65` | `4,263.90` | Fulfilled 5,000 Flyers (`\$637.50`) + 2,000 Poster paper (`\$425.00`) (`\$1,062.50`) for `2025-05-15`; rejected non-catalog `"10,000 tickets"`. |

## Strengths of the Current Implementation

- Accurate Deadline & Stock Validation: The system compares get_supplier_delivery_date against customer deadlines and actively rejects orders that cannot arrive on time (e.g., Requests #13, #15, and #18) with clear explanations.
- Partial Order Fulfillment: Instead of rejecting an entire multi-item request when one item is unavailable or not in the catalog, the system fulfills all available items and explains which ones were excluded.
- Catalog Synonym Resolution: resolve_catalog_item maps informal customer descriptions (e.g., "party streamers", "washi tape") to exact catalog names in paper_supplies, preventing database lookup mismatches.
- Reliable Agent Coordination: Separating inventory, quoting, and transaction tasks across dedicated worker agents keeps tool calls focused and ensures every request completes consistently.

## Areas for Improvement

- Restock Cost vs. Bulk Discount Margin: paper_supplies uses a single unit_price for both supplier restocks and customer sales, so restocking an out-of-stock item at full price and selling it with a bulk discount (5%–15%) slightly reduces net margin on that item.
- Unit-of-Measure Conversion: Packaging units like "500 reams" (Request #3) are passed directly as 500 units at the per-sheet price instead of being converted into total sheets.
- Conservative Handling of Zero-Stock Items: In a few cases (e.g., Requests #5 and #11), the LLM declined items with current_stock: 0 even when supplier restock could have arrived before the customer's deadline.

## Further Improvements

- Margin-Aware Pricing (Wholesale vs. Retail Costs): Separate wholesale supplier costs from retail list prices, or cap bulk discounts on backordered items so restocked orders always maintain a positive profit margin.
- Unit Normalization & Semantic Search: Add a preprocessing step to convert packaging units (reams, packets, boxes) into base units before pricing, and use vector/TF-IDF similarity search over quotes.csv for better historical quote matching.
- Structured Hand-offs & QA Agent: Use Pydantic schemas between worker agents or add a 5th QualityAssuranceAgent to verify that every requested item is accounted for and that all totals and restock eligibility flags are followed consistently.
