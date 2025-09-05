SELECT
  SUM(ss_net_profit) / SUM(ss_ext_sales_price) AS gross_margin,
  i_category,
  i_class,
  GROUPING(i_category) + GROUPING(i_class) AS lochierarchy,
  CAST(RANK() OVER (PARTITION BY GROUPING(i_category) + GROUPING(i_class), CASE WHEN GROUPING(i_class) = 0 THEN i_category END ORDER BY SUM(ss_net_profit) / SUM(ss_ext_sales_price) ASC) AS LONG) AS rank_within_parent /* RANK() is internally represented as *unsigned* int; additional cast is necessary; https://github.com/lakehq/sail/issues/732 */
FROM store_sales
JOIN date_dim AS d1 ON d1.d_date_sk = ss_sold_date_sk
JOIN item ON i_item_sk = ss_item_sk
JOIN store ON s_store_sk = ss_store_sk
WHERE
  d1.d_year = 2002
  AND s_state IN ('AL', 'MI', 'NM', 'NY', 'LA', 'GA', 'PA', 'MN')
GROUP BY
ROLLUP (
  i_category,
  i_class
)
ORDER BY
  lochierarchy DESC,
  CASE WHEN lochierarchy = 0 THEN i_category END, /* Sail does not support using GROUPING() function in ORDER BY clause directly https://github.com/lakehq/sail/issues/731 */
  rank_within_parent
LIMIT 100