"""
db_oracle.py — Conexão e consulta ao banco Oracle (driver thin, sem Oracle Client).
"""
import logging
import oracledb
from config import ORA_USER, ORA_PASS, ORA_DSN

logger = logging.getLogger(__name__)

# Query SQL principal — busca registros de venda de produtos Siemens
QUERY = """
  SELECT '40212903'
             AS distributor_sender_id,
         NVL (RAZAOSOCIALCOMPLETA, 'N/A')
             AS distributor_order_taking_branch_name,
         NVL (CGC, 'N/A')
             AS distributor_order_taking_branch_id,
         NVL (RAZAOSOCIALCOMPLETA, 'N/A')
             AS distributor_ship_from_branch_name,
         NVL (CGC, 'N/A')
             AS distributor_ship_from_branch_id,
         NVL (ENDER.TIPO || ' ' || ENDER.NOMEEND || ' ' || EMP.NUMEND, 'N/A')
             AS distributor_ship_from_address,
         NVL (CID.NOMECID, 'N/A')
             AS distributor_ship_from_city,
         NVL (UFS.DESCRICAO, 'N/A')
             AS distributor_ship_from_state,
         NVL (EMP.CEP, 'N/A')
             AS distributor_ship_from_zip,
         NVL (PAIS.ABREVIATURA, 'N/A')
             AS distributor_ship_from_country,
         NVL (TO_CHAR (CAB.DTENTSAI, 'YYYY-MM-DD'), 'N/A')
             AS distributor_ship_date,
         NVL (TO_CHAR (TRUNC (CAB.DTFATUR), 'YYYY-MM-DD'), 'N/A')
             AS distributor_invoice_date,
         NVL (CAB.NUMNOTA || '-' || CAB.SERIENOTA, 'N/A')
             AS distributor_invoice_number,
         NVL (TO_CHAR (ITE.SEQUENCIA), 'N/A')
             AS distributor_invoice_line_item,
         NVL (PARC.CGC_CPF, 'N/A')
             AS bill_to_customer_record_id,
         NVL (PARC.CGC_CPF, 'N/A')
             AS bill_to_customer_duns_number,
         '000000000'
             AS bill_to_customer_national_reg_number,
         NVL (PARC.RAZAOSOCIAL, 'N/A')
             AS bill_to_customer_name,
         NVL (ENDERPARC.TIPO || ' ' || ENDERPARC.NOMEEND || ' ' || PARC.NUMEND,
              'N/A')
             AS bill_to_customer_billing_address1,
         NVL (PARC.COMPLEMENTO, 'N/A')
             AS bill_to_customer_billing_address2,
         NVL (CIDPARC.NOMECID, 'N/A')
             AS bill_to_customer_city,
         NVL (UFSPARC.DESCRICAO, 'N/A')
             AS bill_to_customer_state,
         NVL (PARC.CEP, 'N/A')
             AS bill_to_customer_zip,
         NVL (PAISPARC.ABREVIATURA, 'N/A')
             AS bill_to_customer_country,
         NVL (PARC.TELEFONE, 'N/A')
             AS bill_to_customer_phone_number,
         NVL (PARC.EMAIL, 'N/A')
             AS bill_to_customer_domain_name_email_address,
         NVL (PARC.CGC_CPF, 'N/A')
             AS ship_to_customer_record_id,
         NVL (PARC.CGC_CPF, 'N/A')
             AS ship_to_customer_duns_number,
         '000000000'
             AS ship_to_customer_national_reg_number,
         NVL (PARC.RAZAOSOCIAL, 'N/A')
             AS ship_to_customer_name,
         NVL (ENDERPARC.TIPO || ' ' || ENDERPARC.NOMEEND || ' ' || PARC.NUMEND,
              'N/A')
             AS ship_to_customer_address1,
         NVL (PARC.COMPLEMENTO, 'N/A')
             AS ship_to_customer_address2,
         NVL (CIDPARC.NOMECID, 'N/A')
             AS ship_to_customer_city,
         NVL (UFSPARC.DESCRICAO, 'N/A')
             AS ship_to_customer_state,
         NVL (PARC.CEP, 'N/A')
             AS ship_to_customer_zip,
         NVL (PAISPARC.ABREVIATURA, 'N/A')
             AS ship_to_customer_country,
         NVL (PARC.TELEFONE, 'N/A')
             AS ship_to_customer_phone_number,
         NVL (PARC.EMAIL, 'N/A')
             AS ship_to_customer_domain_name_email_address,
         NVL (PROD.REFFORN, 'N/A')
             AS vendor_item_number,
         NVL (PROD.DESCRPROD, 'N/A')
             AS item_description,
         NVL (ITE.QTDNEG, 0)
             AS quantity,
         NVL (ITE.CODVOL, 'N/A')
             AS quantity_unit_of_measure,
         NVL (ITE.VLRUNIT, 0)
             AS unit_cost,
         NVL (ITE.VLRTOT, 0)
             AS extended_cost_of_goods_sold,
         NVL (ITE.CODVOL, 'N/A')
             AS cost_unit_of_measure,
         'BRL'
             AS currency_code
    FROM TGFCAB CAB
         INNER JOIN TGFITE ITE ON CAB.NUNOTA = ITE.NUNOTA
         INNER JOIN TSIEMP EMP ON CAB.CODEMP = EMP.CODEMP
         INNER JOIN TSIEND ENDER ON EMP.CODEND = ENDER.CODEND
         INNER JOIN TSICID CID ON EMP.CODCID = CID.CODCID
         INNER JOIN TSIUFS UFS ON CID.UF = UFS.CODUF
         INNER JOIN TSIPAI PAIS ON UFS.CODPAIS = PAIS.CODPAIS
         INNER JOIN TGFPAR PARC ON CAB.CODPARC = PARC.CODPARC
         INNER JOIN TSIEND ENDERPARC ON PARC.CODEND = ENDERPARC.CODEND
         INNER JOIN TSICID CIDPARC ON PARC.CODCID = CIDPARC.CODCID
         INNER JOIN TSIUFS UFSPARC ON CIDPARC.UF = UFSPARC.CODUF
         INNER JOIN TSIPAI PAISPARC ON UFSPARC.CODPAIS = PAISPARC.CODPAIS
         INNER JOIN TGFPRO PROD ON ITE.CODPROD = PROD.CODPROD
   WHERE     CAB.STATUSNOTA = 'L'
         AND CAB.TIPMOV = 'V'
         AND CAB.CODEMP IN (3, 9)
         AND PROD.MARCA = 'SIEMENS'
         AND PROD.ATIVO = 'S'
         AND CAB.DTNEG BETWEEN TO_DATE ('01/01/2024', 'DD/MM/YYYY')
                           AND TO_DATE ('26/04/2026', 'DD/MM/YYYY')
         AND PROD.CODPARCFORN = 52559
ORDER BY CAB.NUNOTA ASC
"""


def get_connection():
    """Cria e retorna uma conexão Oracle (thin mode — sem Oracle Client)."""
    logger.info("Conectando ao Oracle: %s", ORA_DSN)
    conn = oracledb.connect(user=ORA_USER, password=ORA_PASS, dsn=ORA_DSN)
    logger.info("Conexão estabelecida com sucesso.")
    return conn


def fetch_records(progress_callback=None):
    """
    Executa a query e retorna uma lista de dicionários com os registros.

    Args:
        progress_callback: callable(msg: str) — chamado após busca concluída.

    Returns:
        list[dict]: lista de registros mapeados.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        logger.info("Executando query principal…")
        cursor.execute(QUERY)

        columns = [col[0].lower() for col in cursor.description]
        records = []

        for row in cursor:
            record = {}
            for col, val in zip(columns, row):
                # Converte tipos Oracle para Python nativos
                if hasattr(val, 'read'):          # LOB
                    val = val.read()
                elif hasattr(val, 'strftime'):    # date/datetime
                    val = str(val)
                record[col] = val
            records.append(record)

        logger.info("Total de registros encontrados: %d", len(records))
        if progress_callback:
            progress_callback(f"Oracle: {len(records)} registros carregados.")
        return records
    finally:
        cursor.close()
        conn.close()
