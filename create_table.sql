CREATE TABLE desertion."data" (
	periodo varchar NULL,
	codigo_uxxi numeric(10,2) NULL,
	programa varchar NULL,
	codigo_asig varchar NULL,
	asignatura varchar NULL,
	nota_mom1 numeric(10,2) NULL,
	fallas_mom1 numeric(10,2) NULL,
	nota_mom2 numeric(10,2) NULL,
	fallas_mom2 numeric(10,2) NULL,
	nota_mom3 numeric(10,2) NULL,
	fallas_mom3 numeric(10,2) NULL,
	nota_1_momento numeric(10,2) NULL,
	fallas_1_momento numeric(10,2) NULL,
	definitiva numeric(10,2) NULL,
	origen varchar NULL,
	estado varchar NULL,
	promedio_periodo numeric(10,2) NULL,
	promedio_acumulado numeric(10,2) NULL
);

COPY desertion."data"
FROM 'C:\Users\Diego\Documents\csv\2017-1.csv'
DELIMITER ','
CSV header
encoding 'WIN1252';

select codigo_uxxi, 
	   desertion.get_random_name() as nombre,
	   desertion.get_random_lastname() || ' ' ||desertion.get_random_lastname() as apellido
from desertion.data 
where programa='INGENIERÍA DE SISTEMAS' group by codigo_uxxi


create view VW_ingData as
select d.periodo, 
	   d.codigo_uxxi,
 	   s.name_std,
	   s.last_name_std,
	   d.codigo_asig,
	   c.num_credit_crs,
	   d.asignatura,
	   f.name_fdt fundament,
	   d.nota_mom1,
	   d.nota_mom2,
	   d.nota_mom3,
	   d.fallas_mom1,
	   d.fallas_mom2,
	   d.fallas_mom3,
	   d.nota_1_momento,
	   d.fallas_1_momento,
	   d.definitiva,
	   d.origen,
	   d.estado,
	   d.promedio_periodo,
	   d.promedio_acumulado 
from desertion.data d
inner join student s on s.code = d.codigo_uxxi 
inner join course c on c.code = d.codigo_asig 
inner join fundament f on f.idfundament = c.id_fundament 
where programa='INGENIERÍA DE SISTEMAS' 
order by d.periodo 



------------------------------
-- desertion.vw_ingdata_v2 source

CREATE OR REPLACE VIEW desertion.vw_ingdata_v2
AS SELECT d.periodo,
    d.codigo_uxxi AS codigo,
    concat(concat(s.name_std, ' '), s.last_name_std) AS estudiante,
    d.programa,
    f.name_fdt AS nucleo,
    d.codigo_asig,
    d.asignatura,
    d.origen,
    d.promedio_periodo >= 3::numeric AS aprueba_periodo,
    d2.promedio_acumulado AS periodo_anterior,
    d.promedio_acumulado,
    mat.promedio AS promedio_materia_anterior,
    cred.creditos_aprobados,
    d.nota_mom1,
    d.nota_mom2,
    d.nota_mom3,
    d.definitiva,
    d.definitiva >= 3::numeric AS aprueba_materia,
    fall.perdidas_total * 100 / mat.num_cursados AS porcetaje_perdida_materia
   FROM desertion.data d
     LEFT JOIN ( SELECT data.codigo_uxxi,
            data.promedio_acumulado,
            data.numero_periodo
           FROM desertion.data
          GROUP BY data.numero_periodo, data.codigo_uxxi, data.promedio_acumulado) d2 ON (d.numero_periodo - 1) = d2.numero_periodo AND d.codigo_uxxi = d2.codigo_uxxi
     JOIN desertion.student s ON s.code = d.codigo_uxxi
     JOIN desertion.course c ON c.code::text = d.codigo_asig::text
     JOIN desertion.fundament f ON f.idfundament = c.id_fundament
     LEFT JOIN ( SELECT data.codigo_asig,
            data.numero_periodo,
            avg(data.definitiva) AS promedio,
            count(1) AS num_cursados
           FROM desertion.data
          GROUP BY data.codigo_asig, data.numero_periodo) mat ON (d.numero_periodo - 1) = mat.numero_periodo AND d.codigo_asig::text = mat.codigo_asig::text
     LEFT JOIN ( SELECT d_1.codigo_uxxi,
            sum(c_1.num_credit_crs) AS creditos_aprobados
           FROM desertion.data d_1
             JOIN desertion.course c_1 ON c_1.code::text = d_1.codigo_asig::text
          WHERE d_1.definitiva >= 3::numeric
          GROUP BY d_1.codigo_uxxi) cred ON cred.codigo_uxxi = d.codigo_uxxi
     LEFT JOIN ( SELECT data.codigo_asig,
            data.numero_periodo,
            count(1) AS perdidas_total
           FROM desertion.data
          WHERE data.definitiva < 3::numeric
          GROUP BY data.codigo_asig, data.numero_periodo) fall ON (d.numero_periodo - 1) = fall.numero_periodo AND d.codigo_asig::text = fall.codigo_asig::text
  WHERE d.programa::text = 'INGENIERÍA DE SISTEMAS'::text
  ORDER BY d.periodo, d.codigo_uxxi;