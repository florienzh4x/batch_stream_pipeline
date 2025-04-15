select
	s.store_id,
	p2.product_id,
	t.transaction_id,
	s.store_name,
	p2.product_name,
	p2.brand,
	p2.category,
	t.quantity,
	t.total_price,
	t.transaction_date,
    CURRENT_TIMESTAMP AS ingest_time
from transactions t 
left join stores s 
on t.store_id = s.store_id
left join orders o 
on t.order_id = o.order_id
left join payments p 
on t.payment_id = p.payment_id
left join products p2 
on t.product_id = p2.product_id
where 
	p.payment_status = 'Completed' and
	o.order_status = 'Completed'