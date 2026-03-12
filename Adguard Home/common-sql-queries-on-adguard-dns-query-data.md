## Common SQL queries for DNS query data in MariaDB

### To find out the time span of the database
SELECT FLOOR(diff / 86400) AS days, FLOOR((diff % 86400) / 3600) AS hours, FLOOR((diff % 3600) / 60) AS minutes, diff % 60 AS seconds FROM ( SELECT TIMESTAMPDIFF(SECOND, MIN(`time`), MAX(`time`)) AS diff FROM `querylog` ) t;

### List blocked queries and group by hostname order by most requests
SELECT *, COUNT(`hostname`) AS `hostname_count` FROM `querylog` WHERE `blocked`=1 GROUP BY `hostname` ORDER BY `hostname_count` DESC;

