import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

## read data
product = pd.read_csv('products.csv')
department = pd.read_csv('departments.csv')
aisle = pd.read_csv('aisles.csv')
order = pd.read_csv('orders.csv').drop('eval_set', axis=1)
order['days_since_prior_order'] = order['days_since_prior_order'].fillna(0)
order_item = pd.read_csv('instacart_transaction.csv')

## how many products contained in each order
print('Products per order:', (order_item.product_id.count() / order.order_id.count()))

## how many products bought by each customer
print('Products per customer:', order_item.product_id.count() / len(order.user_id.unique()))

## how many orders made by each customer
print('Orders per customer:', order.order_id.count() / len(order.user_id.unique()))

## plot orders made on each day of week
order_dow = order.groupby('order_dow').count()
dow = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
plt.figure(figsize=(8,6))
plt.plot(dow, order_dow['order_id'], c='black')
plt.xticks(rotation=90)
plt.ylabel('Number of orders',fontsize=12)
plt.title('Days of week', fontsize=15)

## plot orders made on each hour of day every day of week
order_hour_of_day = order.groupby('order_hour_of_day').count()
time = range(24)
plt.figure(figsize=(8,6))
for day in range(7):
    order_by_hour = []
    for hour in time:
        order_by_hour.append(len(order[(order['order_dow']==day) & (order['order_hour_of_day']==hour)]))
    plt.plot(time, order_by_hour, label=dow[day])
    plt.legend(fontsize=12)
plt.tick_params(labelsize=12)
plt.xlabel('Hours', fontsize=15)
plt.ylabel('Number of Orders', fontsize=15)
plt.title('Hours of Day', fontsize=15)

## merge the dataframe with products as indexed
product = product.set_index('product_id')

product = pd.merge(left=product, right = order_item.groupby('product_id').order_id.count().to_frame('total_order'),
                  left_index=True, right_index=True)
product = pd.merge(left=product, right=order_item.groupby('product_id').reordered.sum().to_frame('total_reorder'),
                  left_index=True, right_index=True)

product['reorder_ratio'] = product['total_reorder']/product['total_order']

## extract top 25 ordered product and plot the graph
order_top = product.sort_values(by='total_order', ascending=False)[:25]
plt.figure(figsize=(8,6))
plt.bar(order_top.index.map(str), order_top['total_order'], color='tab:orange')
plt.ylabel('Total Order', fontsize=15)
plt.title('Top 25 Ordered Items', fontsize=20)
plt.xticks(rotation=90)

## create the reorder attribute and plot the top 25 reordered products
reorder_top = product.sort_values(by='reorder_ratio', ascending=False)[:25]
plt.figure(figsize=(8,6))
plt.plot(reorder_top.index.map(str), reorder_top['reorder_ratio'], color='tab:orange')
plt.ylabel('Reorder Ratio', fontsize=15)
plt.title('Top 25 Reordered Items', fontsize=20)
plt.xticks(rotation=90)

## merge the dataframe with departments as indexed
department = pd.read_csv('departments.csv')
department = department.set_index('department_id')
## total orders made in each department
department = pd.merge(left=department, 
                      right=product.groupby('department_id').total_order.sum().to_frame('total_order'),
                     left_index=True, right_index=True)
## total reorders made in each department
department = pd.merge(left=department, 
                      right=product.groupby('department_id').total_reorder.sum().to_frame('total_reorder'),
                     left_index=True, right_index=True)
## reordered ratio of each department 
department['reorder_ratio'] = department['total_reorder']/department['total_order']
## total products contained in each department
department = pd.merge(left=department, 
                      right=product.groupby('department_id').product_name.count().to_frame('items'),
                     left_index=True, right_index=True)

## plot the number of items in each department
plt.figure(figsize=(8,6))
sns.barplot(department['department'], department['items'], color='tab:blue')
plt.ylabel('Number of items', fontsize=15)
plt.title('Number of items in each department', fontsize=20)
plt.xticks(rotation=90)

## plot total orders made in each department
department_sort = department.sort_values(by='total_order', ascending=False)
plt.figure(figsize=(8,6))
sns.barplot(department_sort['department'], department_sort['total_order'], color='tab:blue')
plt.ylabel('Number of orders', fontsize=15)
plt.title('Department Sale', fontsize=20)
plt.xticks(rotation=90)

## plot percentiles of each deparment sale
department_ratio = department_sort['total_order']/department_sort['total_order'].sum()
plt.figure(figsize=(16,12))
plt.pie(department_ratio, labels=department_sort['department'], autopct='%1.1f%%')
plt.title('Department Sale', fontsize=15)

## reorder ratio of each department
department_reorder_ratio = department.sort_values(by='reorder_ratio', ascending=False)
plt.figure(figsize=(8,6))
plt.plot(department_reorder_ratio['department'], 
         department_reorder_ratio['reorder_ratio'], color='tab:blue')
plt.ylabel('Reorder Ratio', fontsize=15)
plt.title('Department Reorder Ratio', fontsize=20)
plt.xticks(rotation=90)

## merge user subdataframe 
user_items = order.groupby('user_id').order_number.count().to_frame('total_items')
user_items = user_items.reset_index()
user_items['customer'] = None
## make simple categories of customer
user_items.loc[user_items['total_items'] >= 50, ['customer']] = 'Addicted'
user_items.loc[(user_items['total_items'] < 50) & (user_items['total_items'] >= 20), ['customer']] = 'Heavy'
user_items.loc[(user_items['total_items'] < 20) & (user_items['total_items'] >= 10), ['customer']] = 'Medium'
user_items.loc[(user_items['total_items'] < 10) & (user_items['total_items'] >= 0), ['customer']] = 'Light'
## plot categories percentile 
plt.figure(figsize=(16,12))
user_group = user_items.groupby('customer').user_id.count().to_frame('number_of_users')
user_group = user_group.reset_index()
user_ratio = user_group['number_of_users']/user_group['number_of_users'].sum()
plt.pie(user_ratio, labels=user_group['customer'], autopct='%1.1f%%')
plt.title('Customers category', fontsize=15)

## plot the order frequency
order = order.astype({'days_since_prior_order': 'int32'})
user_days = order.groupby('days_since_prior_order').user_id.count().to_frame('total_user')
user_days = user_days.reset_index()
plt.figure(figsize=(8,6))
sns.barplot(user_days['days_since_prior_order'], user_days['total_user'], color='tab:cyan')
plt.title('Order Frequency', fontsize=14)
plt.xlabel('Days since prior order',fontsize=10)
plt.ylabel('Number of users',fontsize=10)
plt.xticks(rotation=90)


# In[ ]:




