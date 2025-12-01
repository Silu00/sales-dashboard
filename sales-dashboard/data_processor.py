import os
import re
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def process_data(folder_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_users = os.path.join(base_dir, folder_name, 'users.csv')
    path_orders = os.path.join(base_dir, folder_name, 'orders.parquet')
    path_books = os.path.join(base_dir, folder_name, 'books.yaml')

    df_users = pd.read_csv(path_users, dtype={'phone': str})
    df_orders = pd.read_parquet(path_orders)
    with open(path_books, 'r', encoding='utf-8') as file:
        data_books = yaml.safe_load(file)

    df_users = df_users.drop_duplicates()

    def cleaning_phone(phone):
        if pd.isna(phone):
            return phone
        return re.sub(r'\D', '', str(phone))

    df_users['phone'] = df_users['phone'].apply(cleaning_phone)

    def cleaning_price(unit_price):
        if pd.isna(unit_price):
            return 0.0
        s = str(unit_price).strip()
        is_euro = ('EUR' in s) or ('€' in s)
        s = s.replace('¢', '.').replace(',', '.')
        clean_price_num = re.sub(r'[^\d.]', '', s)
        try:
            val = float(clean_price_num)
        except ValueError:
            val = 0.0
        return round(val * 1.2, 2) if is_euro else val

    df_orders['unit_price'] = df_orders['unit_price'].apply(cleaning_price)
    df_orders['quantity'] = pd.to_numeric(df_orders['quantity'], errors='coerce').fillna(0)
    df_orders['paid_price'] = df_orders['unit_price'] * df_orders['quantity']

    def fix_timestamp(timestamp):
        if pd.isna(timestamp):
            return timestamp
        s = str(timestamp).strip()
        s = re.sub(r'[T,;]', ' ', s)
        s = re.sub(r'(?i)([ap])\.m\.', r'\1m', s)
        return re.sub(r'\s+', ' ', s)

    df_orders['timestamp'] = df_orders['timestamp'].apply(fix_timestamp)
    df_orders['parsed_date'] = pd.to_datetime(
        df_orders['timestamp'], format='mixed', dayfirst=False, errors='coerce'
    )
    df_orders['year'] = df_orders['parsed_date'].dt.year
    df_orders['month'] = df_orders['parsed_date'].dt.month
    df_orders['day'] = df_orders['parsed_date'].dt.day

    df_books = pd.DataFrame(data_books)
    df_books.columns = [col.replace(':', '') for col in df_books.columns]

    def cleaned_text(text):
        if pd.isna(text):
            return np.nan
        s = str(text).strip()
        if s in ['NULL', 'null', '<null>', '-', '\t', '""', "''", '', '" "', "' '"]:
            return np.nan
        return s

    for col in ['title', 'author', 'genre', 'publisher']:
        df_books[col] = df_books[col].apply(cleaned_text)

    df_books['id'] = pd.to_numeric(df_books['id'], errors='coerce')
    df_books = df_books.dropna(subset=['id']).drop_duplicates(subset=['id'])

    daily_revenue = df_orders.groupby(['year', 'month', 'day'])['paid_price'].sum().reset_index()
    daily_revenue = daily_revenue.rename(columns={'paid_price': 'revenue'})
    daily_revenue['date_obj'] = pd.to_datetime(daily_revenue[['year', 'month', 'day']])
    daily_revenue['date_str'] = daily_revenue['date_obj'].dt.strftime('%Y-%m-%d')
    daily_revenue = daily_revenue.sort_values('date_obj')

    top_5_days = daily_revenue.sort_values(by=['revenue'], ascending=False).head(5)[['date_str', 'revenue']]

    df_u = df_users.reset_index(drop=True)
    df_u['name_clean'] = df_u['name'].astype(str).str.lower().str.strip()
    df_u['address_clean'] = df_u['address'].astype(str).str.lower().str.strip()
    df_u['phone_clean'] = df_u['phone'].astype(str).str.strip()

    parent = list(range(len(df_u)))

    def find(i):
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    cols_combinations = [
        ['name_clean', 'address_clean'],
        ['name_clean', 'phone_clean'],
        ['address_clean', 'phone_clean']
    ]

    for cols in cols_combinations:
        if not all(col in df_u.columns for col in cols):
            continue

        for key, indices in df_u.groupby(cols).indices.items():
            key_list = [key] if not isinstance(key, tuple) else key
            if any(str(k) in ['nan', '', 'null', 'None'] for k in key_list):
                continue
            if len(indices) > 1:
                base = indices[0]
                for other in indices[1:]:
                    union(base, other)

    unique_users_count = sum(1 for i in range(len(df_u)) if parent[i] == i)

    def get_author_set(author_str):
        if pd.isna(author_str):
            return None
        parts = str(author_str).split(',')
        authors = [p.strip() for p in parts if p.strip()]
        authors.sort()
        return tuple(authors)

    df_books['author_set'] = df_books['author'].apply(get_author_set)
    unique_authors_count = df_books['author_set'].nunique()

    df_merged = df_orders.merge(df_books, left_on='book_id', right_on='id', how='inner')
    most_popular = df_merged.groupby('author_set')['quantity'].sum().reset_index()

    top_author_str = "No Data"
    if not most_popular.empty:
        top_row = most_popular.sort_values(by=['quantity'], ascending=False).iloc[0]
        top_author_str = ", ".join(top_row['author_set'])

    df_u['group_id'] = [find(i) for i in range(len(df_u))]
    user_to_group = dict(zip(df_u['id'], df_u['group_id']))
    df_orders['group_id'] = df_orders['user_id'].map(user_to_group)

    top_customer_aliases = []
    grouped_spending = df_orders.dropna(subset=['group_id']).groupby('group_id')['paid_price'].sum()
    if not grouped_spending.empty:
        top_group_id = grouped_spending.idxmax()
        top_customer_aliases = df_u[df_u['group_id'] == top_group_id]['id'].tolist()

    with plt.style.context('dark_background'):
        fig, ax = plt.subplots(figsize=(10, 5))

        bg_color = '#0E1117'
        text_color = '#E0E0E0'
        line_color = '#5D9FD8'

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        ax.plot(
            daily_revenue['date_obj'],
            daily_revenue['revenue'],
            marker='o',
            markersize=4,
            linestyle='-',
            linewidth=1.5,
            color=line_color,
            alpha=0.9
        )

        ax.set_title('Daily Revenue', color=text_color, fontsize=14, pad=15)
        ax.set_xlabel('Date', color=text_color)
        ax.set_ylabel('USD', color=text_color)

        ax.grid(True, linestyle=':', linewidth=0.5, color='#FFFFFF', alpha=0.2)
        ax.tick_params(axis='both', colors=text_color, which='both')
        plt.xticks(rotation=45)

        for spine in ax.spines.values():
            spine.set_edgecolor(text_color)
            spine.set_alpha(0.3)

        plt.tight_layout()

    return {
        "top_5_days": top_5_days,
        "unique_users": unique_users_count,
        "unique_authors": unique_authors_count,
        "top_author": top_author_str,
        "best_buyer_ids": top_customer_aliases,
        "chart_fig": fig
    }