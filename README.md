# 📊 Sales Data Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sales-dashboard-project.streamlit.app/)

A comprehensive data analysis dashboard built with Streamlit and Pandas. This application processes raw sales data, performs advanced entity resolution (user reconciliation), converts currencies, and visualizes revenue trends across multiple distinct datasets.

## 🔗 Live Demo
**Access the dashboard here:** [https://sales-dashboard-project.streamlit.app/](https://sales-dashboard-project.streamlit.app/)

## 🎯 Project Objectives

The goal of this project was to build a reusable data pipeline to analyze three separate data folders (`DATA1`, `DATA2`, `DATA3`) with the following specific requirements:

1.  **Data Ingestion & Cleaning:**
    * Parsing dates correctly handling various formats.
    * Handling duplicated, missing, or malformed values.
    * Type casting (integers, floats, datetime objects).
2.  **Transformation:**
    * **Currency Standardization:** Converting all prices to USD ($) using a fixed rate (€1 = $1.2).
    * **Revenue Calculation:** Computing `paid_price = quantity * unit_price`.
3.  **Advanced Analytics:**
    * **User Reconciliation:** Identifying "real" unique users even if they changed one attribute (e.g., address, phone, or alias). The system links records to identify the true top customer.
    * **Author Set Analysis:** Distinguishing between individual authors and collaborative groups (e.g., "John & Paul" is a distinct set from "John").
4.  **Visualization:**
    * Interactive daily revenue charts.
    * Top metrics display.

## ⚙️ Solution Logic

### User Reconciliation (Entity Resolution)
The most complex part of the task was identifying unique users who change only one contact detail at a time.
* **Approach:** The application implements a graph-based or transitive linking logic. If User A shares an email with User B, and User B shares a phone number with User C, they are all resolved to a single unique Identity ID.
* **Result:** This allows for an accurate calculation of the "Top Customer by Total Spending," aggregating purchases across all their aliases.

### Dashboard Structure
The Streamlit app is organized into **Tabs** corresponding to each data folder (`DATA1`, `DATA2`, `DATA3`). Each tab independently calculates and displays:

* **Top 5 Days by Revenue:** Formatted as `YYYY-MM-DD`.
* **Real Unique Users:** Count after reconciliation.
* **Unique Author Sets:** Distinct combinations of co-authors.
* **Most Popular Author(s):** By sold book count.
* **Best Buyer:** Displays the total spent and an array of all associated `user_id`s (e.g., `[id1, id2, ...]`).
* **Daily Revenue Chart:** A Line chart visualizing sales trends over time.

## 🛠️ Tech Stack

* **Python 3.9+**
* **Streamlit:** Frontend & UI.
* **Pandas:** Data manipulation and cleaning.
* **NetworkX (Optional/Implicit):** Used logic similar to connected components for user reconciliation.
* **Matplotlib / Altair:** For plotting revenue charts.

## 📂 Repository Structure

* `app.py` - Main application entry point containing the dashboard layout.
* `data_processing.py` - Core logic for cleaning, currency conversion, and entity resolution.
* `DATA1/`, `DATA2/`, `DATA3/` - Folders containing the raw CSV/JSON input files.
