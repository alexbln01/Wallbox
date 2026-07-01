-- Excel Fertigungsliste (CRPlus / MSSQL)
-- Korrigierte Fassung, Stand 01.07.2026
-- Basis: Version vom 21.05.2026 (NOLOCK, M. Jansen / Connedata),
-- ergänzt um die in dieser Version verloren gegangenen Fixes vom 18.05.2026:
--   * "Heften am" matcht auch Arbeitsschritte mit "Schweißen"
--   * Spalte Versandbereit-Menge (adt_nversandbereit) wieder enthalten
-- sowie:
--   * COALESCE für ADZ_LRESTBESTAND, damit Positionen ohne adtzusatz-Datensatz
--     nicht aus der Liste fallen

SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
       vertrieb.auf_nid,
       vertrieb.auf_cfaufnr AS [Auftrags-Nr.],
       verAdt.ADT_NPOS AS [Pos.],
       kunde.ADR_CMATCH AS [Kunde],
       IIF(verAdt.ADT_CKONR = '', vertrieb.AUF_CKONR, verAdt.ADT_CKONR) AS [Bestell-Nr.],
       prodAuf.AUF_CFAUFNR AS [Prod. Auftrag],
       fertauftrag.FAR_NEXTID AS [Lohnschein],
       verAdt.ADT_CARTNR AS [Artikel-Nr.],
       verAdt.adt_cprodukt AS [Bezeichnung],
       NULLIF(CONVERT(date, verAdt.ADT_DLDATE), CONVERT(date, '19000101')) AS [Best. Liefertermin],
       verAdt.ADT_NMENGE AS [bestellte Menge],
       prodadt.ADT_NMENGE AS [Menge Produktion],
       verAdt.ADT_NGELIEFERT AS [gelieferte Menge],
       verAdt.ADT_NMENGE - verAdt.ADT_NGELIEFERT AS [offene Menge],
       NULLIF(CONVERT(date, prodAdt.adt_dgepackt), CONVERT(date, '19000101')) AS [Vollständig gepackt am],
       NULLIF(CONVERT(date, prodAdt.adt_dversandbereit), CONVERT(date, '19000101')) AS [Versandbereit am],
       prodAdt.adt_nversandbereit AS [Versandbereit Menge],
       (SELECT MIN(NULLIF(CONVERT(date, sol.sol_dfert), CONVERT(date, '19000101')))
             FROM sollzeit sol WITH (NOLOCK)
             INNER JOIN arbeitsschritte arb WITH (NOLOCK)
                 ON arb.arb_nid = sol.sol_narbid
             WHERE sol.sol_nartid = prodAdt.adt_nartid
               AND (arb.arb_ckbez LIKE '%Heften%' OR arb.arb_ckbez LIKE '%Schweißen%')) AS [Heften am],
       (SELECT TOP 1 NULLIF(CONVERT(date, sol.sol_dfert), CONVERT(date, '19000101'))
             FROM sollzeit sol WITH (NOLOCK)
             INNER JOIN arbeitsschritte arb WITH (NOLOCK)
                    ON arb.arb_nid = sol.sol_narbid
             WHERE sol.sol_nartid = prodAdt.adt_nartid
                AND sol.sol_nferid = 7
             ORDER BY sol.sol_dfert ASC, sol.sol_nid ASC) AS [Beschichten am],
       (SELECT TOP 1
              IIF(NULLIF(CONVERT(date, sol.sol_dfert), CONVERT(date, '19000101')) IS NULL,
                    NULL,
                    arb.arb_ckbez)
             FROM sollzeit sol WITH (NOLOCK)
             INNER JOIN arbeitsschritte arb WITH (NOLOCK)
                    ON arb.arb_nid = sol.sol_narbid
             WHERE sol.sol_nartid = prodAdt.adt_nartid
                AND sol.sol_nferid = 7
             ORDER BY sol.sol_dfert ASC, sol.sol_nid ASC) AS [Beschichtung],
       lieferant.ADR_CMATCH AS [Beschichter],
       bdt_npos AS [Beistell-Pos],
       bdt_nmenge AS [Beistell-Menge],
       BES_NEXTID AS [Beistell-LS],
       NULLIF(CONVERT(date, bestell.BES_DBDATE), CONVERT(date, '19000101')) AS [Tat. Beistellung],
       (SELECT MIN(NULLIF(CONVERT(date, sub.ist_ddatum), CONVERT(date, '19000101')))
             FROM (
                    SELECT
                            ist.IST_DDATUM,
                           SUM(tag.TAG_NIST) OVER (ORDER BY ist.IST_DDATUM ASC, ist.IST_NID ASC) AS kumuliert
                    FROM istzeit2 ist WITH (NOLOCK)
                    INNER JOIN arbeitsschritte arb WITH (NOLOCK) ON ist.IST_NARBID = arb.arb_nid
                    INNER JOIN tagplan tag WITH (NOLOCK) ON ist.IST_NTAGID = tag.tag_nid
                    WHERE ist.IST_NADTID = prodAdt.adt_nid
                       AND arb.ARB_CKBEZ LIKE '%schweißen%'
                       AND ist.IST_NART = 2
             ) sub
             WHERE sub.kumuliert >= prodAdt.ADT_NMENGE
       ) AS [Schweißen Ende]
FROM auftrag vertrieb WITH (NOLOCK)
INNER JOIN adresse AS kunde WITH (NOLOCK) ON kunde.ADR_NID = vertrieb.AUF_NADRID
INNER JOIN auftragdetail AS verAdt WITH (NOLOCK) ON verAdt.ADT_NAUFID = vertrieb.auf_nid
LEFT JOIN auftragdetail AS prodAdt WITH (NOLOCK)
    INNER JOIN auftrag AS prodAuf WITH (NOLOCK)
        ON prodAdt.ADT_NAUFID = prodAuf.auf_nid
       AND prodAuf.AUF_NSTATUS = 11
       AND prodAuf.AUF_LPROD = 1
    ON prodAdt.adt_nadtid5 = verAdt.adt_nid
   AND prodAdt.ADT_LPLANOK = 0
LEFT JOIN adtzusatz WITH (NOLOCK) ON ADZ_NADTID = verAdt.ADT_NID
LEFT JOIN bestelldetails WITH (NOLOCK)
       INNER JOIN bestell WITH (NOLOCK) ON bestell.bes_nid = BDT_NBESID AND BES_NSTATUS = 6
       ON BDT_NADTID = prodAdt.adt_nid
LEFT JOIN adresse AS lieferant WITH (NOLOCK) ON BES_NADRID = lieferant.adr_nid
LEFT JOIN fertauftrag WITH (NOLOCK) ON FAR_NADTID = prodAdt.adt_nid
WHERE vertrieb.AUF_LBER = 0
      AND vertrieb.AUF_NSTATUS = 11
      AND vertrieb.AUF_LPROD = 0
      AND verAdt.ADT_NGELIEFERT < verAdt.ADT_NMENGE
      AND vertrieb.AUF_LOHNE = 0
      AND vertrieb.AUF_LREV = 0
      AND verAdt.ADT_LOBER = 0
      AND vertrieb.AUF_LSTORNO = 0
      AND verAdt.ADT_LSTORNO = 0
      AND COALESCE(ADZ_LRESTBESTAND, 0) = 0
      AND COALESCE(prodAuf.AUF_LBER, 0) = 0
      AND COALESCE(prodAdt.ADT_LPLANOK, 0) = 0;
