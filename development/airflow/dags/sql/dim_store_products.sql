select 
	s.store_id,
	p.product_id,
	s.store_name,
	p.product_name,
	p.brand,
	p.category,
    CURRENT_TIMESTAMP AS ingest_time
from products p 
left join stores s 
on p.store_id = s.store_id