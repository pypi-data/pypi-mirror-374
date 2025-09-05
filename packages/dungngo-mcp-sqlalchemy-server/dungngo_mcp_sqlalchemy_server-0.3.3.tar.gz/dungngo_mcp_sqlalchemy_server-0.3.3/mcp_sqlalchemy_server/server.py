from collections import defaultdict
import os
import logging
from dotenv import load_dotenv
import pyodbc
from typing import Any, Dict, List, Optional
import json

from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve database connection details from environment variables
DB_UID = os.getenv("ODBC_USER")
DB_PWD = os.getenv("ODBC_PASSWORD")
DB_DSN = os.getenv("ODBC_DSN")
MAX_LONG_DATA = int(os.getenv("MAX_LONG_DATA",4096))
API_KEY = os.getenv("API_KEY", "none")

### Database ###


def get_connection(readonly=True, uid: Optional[str] = None, pwd: Optional[str] = None, 
                dsn: Optional[str] = None) -> pyodbc.Connection:
    dsn = DB_DSN if dsn is None else dsn
    uid = DB_UID if uid is None else uid
    pwd = DB_PWD if pwd is None else pwd

    if dsn is None:
        raise ValueError("ODBC_DSN environment variable is not set.")
    if uid is None:
        raise ValueError("ODBC_USER environment variable is not set.")
    if pwd is None:
        raise ValueError("ODBC_PASSWORD environment variable is not set.")

    dsn_string = f"DSN={dsn};UID={uid};PWD={pwd}"
    logging.info(f"DSN:{dsn}  UID:{uid}")
    # connection_string="DSN=VOS;UID=dba;PWD=dba"

    return pyodbc.connect(dsn_string, autocommit=True, readonly=readonly)


### Constants ###


### MCP ###
mcp = FastMCP('mcp-sqlalchemy-server', transport=["stdio", "sse"])

@mcp.tool(
    name="podbc_get_schemas",
    description="Retrieve and return a list of all schema names from the connected database."
)
def podbc_get_schemas(user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Retrieve and return a list of all schema names from the connected database.

    Args:
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: A list of schema names.
    """
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.tables(table=None, catalog="%", schema=None, tableType=None);
            catalogs = {row[0] for row in rs.fetchall()}
            return json.dumps(list(catalogs))

    except pyodbc.Error as e:
        logging.error(f"Error retrieving schemas: {e}")
        raise


@mcp.tool(
    name="podbc_get_tables",
    description="Retrieve and return a list containing information about tables in specified schema, if empty uses connection default"
)
def podbc_get_tables(Schema: Optional[str] = None, user:Optional[str]=None, 
                    password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Retrieve and return a list containing information about tables.

    If `schema` is None, returns tables for all schemas.
    If `schema` is not None, returns tables for the specified schema.

    Args:
        schema (Optional[str]): The name of the schema to retrieve tables for. If None, retrieves tables for all schemas.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: A list containing information about tables.
    """
    cat = "%" if Schema is None else Schema
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.tables(table=None, catalog=cat, schema="%", tableType="TABLE");
            results = []
            for row in rs:
                results.append({"TABLE_CAT":row[0], "TABLE_SCHEM":row[1], "TABLE_NAME":row[2]})
                
            return json.dumps(results, indent=2)
    except pyodbc.Error as e:
        logging.error(f"Error retrieving tables: {e}")
        raise
        

@mcp.tool(
    name="podbc_describe_table",
    description="Retrieve and return a dictionary containing the definition of a table, including column names, data types, nullable,"
                " autoincrement, primary key, and foreign keys."
)
def podbc_describe_table(Schema:str, table: str, user:Optional[str]=None, 
                        password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Retrieve and return a dictionary containing the definition of a table, including column names, data types, nullable, autoincrement, primary key, and foreign keys.

    If `schema` is None, returns the table definition for the specified table in all schemas.
    If `schema` is not None, returns the table definition for the specified table in the specified schema.

    Args:
        schema (str): The name of the schema to retrieve the table definition for. If None, retrieves the table definition for all schemas.
        table (str): The name of the table to retrieve the definition for.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: A dictionary containing the table definition, including column names, data types, nullable, autoincrement, primary key, and foreign keys.
    """
    cat = "%" if Schema is None else Schema
    table_definition = {}
    try:
        with get_connection(True, user, password, dsn) as conn:
            rc, tbl = _has_table(conn, cat=cat, table=table)
            if rc:
                table_definition = _get_table_info(conn, cat=tbl.get("cat"), sch=tbl.get("sch"), table=tbl.get("name"))

        return json.dumps(table_definition, indent=2)

    except pyodbc.Error as e:
        logging.error(f"Error retrieving table definition: {e}")
        raise


def _has_table(conn, cat:str, table:str):
    with conn.cursor() as cursor:
        row = cursor.tables(table=table, catalog=cat, schema=None, tableType=None).fetchone()
        if row:
            return True, {"cat":row[0], "sch": row[1], "name":row[2]}
        else:
            return False, {}


def _get_columns(conn, cat: str, sch: str, table:str):
    with conn.cursor() as cursor:
        ret = []
        for row in cursor.columns(table=table, catalog=cat, schema=sch):
            ret.append({
                "name":row[3],
                "type":row[5],
                "column_size": row[6],
                # "decimal_digits":row[8],
                "num_prec_radix":row[9],
                "nullable":False if row[10]==0 else True,
                "default":row[12]
            })
        return ret


def _get_pk_constraint(conn, cat: str, sch: str, table:str):
    with conn.cursor() as cursor:
        ret = None
        rs = cursor.primaryKeys(table=table, catalog=cat, schema=sch).fetchall()
        if len(rs) > 0:
            ret = { "constrained_columns": [row[3] for row in rs],
                "name": rs[0][5]
            }
        return ret


def _get_foreign_keys(conn, cat: str, sch: str, table:str):
    def fkey_rec():
        return {
            "name": None,
            "constrained_columns": [],
            "referred_cat": None,
            "referred_schem": None,
            "referred_table": None,
            "referred_columns": [],
            "options": {},
        }

    fkeys = defaultdict(fkey_rec)
    with conn.cursor() as cursor:
        rs = cursor.foreignKeys(foreignTable=table, foreignCatalog=cat, foreignSchema=sch)
        for row in rs:
            rec = fkeys[row[11]]  #.FK_NAME
            rec["name"] = row[11] #.FK_NAME

            c_cols = rec["constrained_columns"]
            c_cols.append(row[7]) #.FKCOLUMN_NAME)

            r_cols = rec["referred_columns"]
            r_cols.append(row[3]) #.PKCOLUMN_NAME)

            if not rec["referred_table"]:
                rec["referred_table"] = row[2]  #.PKTABLE_NAME
                rec["referred_schem"] = row[1] #.PKTABLE_OWNER
                rec["referred_cat"] = row[0] #.PKTABLE_CAT

    return list(fkeys.values())


def _get_table_info(conn, cat:str, sch: str, table: str) -> Dict[str, Any]:
    try:
        columns = _get_columns(conn, cat=cat, sch=sch, table=table)
        primary_keys = _get_pk_constraint(conn, cat=cat, sch=sch, table=table)['constrained_columns']
        foreign_keys = _get_foreign_keys(conn, cat=cat, sch=sch, table=table)

        table_info = {
            "TABLE_CAT": cat,
            "TABLE_SCHEM": sch,
            "TABLE_NAME": table,
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys
        }

        for column in columns:
            column["primary_key"] = column['name'] in primary_keys

        return table_info

    except pyodbc.Error as e:
        logging.error(f"Error retrieving table info: {e}")
        raise


@mcp.tool(
    name="podbc_filter_table_names",
    description="Retrieve and return a list containing information about tables whose names contain the substring 'q' ."
)
def podbc_filter_table_names(q: str, Schema: Optional[str] = None, user:Optional[str]=None, password:Optional[str]=None, 
                            dsn:Optional[str]=None) -> str:
    """
    Retrieve and return a list containing information about tables whose names contain the substring 'q'

    Args:
        q (str): The substring to filter table names by.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: A list containing information about tables whose names contain the substring 'q'.
    """
    cat = "%" if Schema is None else Schema
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.tables(table=None, catalog=cat, schema='%', tableType="TABLE");
            results = []
            for row in rs:
                if q in row[2]:
                    results.append({"TABLE_CAT":row[0], "TABLE_SCHEM":row[1], "TABLE_NAME":row[2]})

            return json.dumps(results, indent=2)
    except pyodbc.Error as e:
        logging.error(f"Error filtering table names: {e}")
        raise


@mcp.tool(
    name="podbc_execute_query",
    description="Execute a SQL query and return results in JSONL format."
)
def podbc_execute_query(query: str, max_rows: int = 100, params: Optional[Dict[str, Any]] = None,
                  user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SQL query and return results in JSONL format.

    Args:
        query (str): The SQL query to execute.
        max_rows (int): Maximum number of rows to return. Default is 100.
        params (Optional[Dict[str, Any]]): Optional dictionary of parameters to pass to the query.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in JSONL format.
    """
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.execute(query) if params is None else cursor.execute(query, params)
            columns = [column[0] for column in rs.description]            
            results = []
            for row in rs:
                rs_dict = dict(zip(columns, row))
                truncated_row = {key: (str(value)[:MAX_LONG_DATA] if value is not None else None) for key, value in rs_dict.items()}
                results.append(truncated_row)                
                if len(results) >= max_rows:
                    break
                
            # Convert the results to JSONL format
            jsonl_results = "\n".join(json.dumps(row) for row in results)

            # Return the JSONL formatted results
            return jsonl_results
    except pyodbc.Error as e:
        logging.error(f"Error executing query: {e}")
        raise


@mcp.tool(
    name="podbc_execute_query_md",
    description="Execute a SQL query and return results in Markdown table format."
)
def podbc_execute_query_md(query: str, max_rows: int = 100, params: Optional[Dict[str, Any]] = None, 
                     user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SQL query and return results in Markdown table format.

    Args:
        query (str): The SQL query to execute.
        max_rows (int): Maximum number of rows to return. Default is 100.
        params (Optional[Dict[str, Any]]): Optional dictionary of parameters to pass to the query.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in Markdown table format.
    """
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.execute(query) if params is None else cursor.execute(query, params)
            columns = [column[0] for column in rs.description]            
            results = []
            for row in rs:
                rs_dict = dict(zip(columns, row))
                truncated_row = {key: (str(value)[:MAX_LONG_DATA] if value is not None else None) for key, value in rs_dict.items()}
                results.append(truncated_row)                
                if len(results) >= max_rows:
                    break
                
            # Create the Markdown table header
            md_table = "| " + " | ".join(columns) + " |\n"
            md_table += "| " + " | ".join(["---"] * len(columns)) + " |\n"

            # Add rows to the Markdown table
            for row in results:
                md_table += "| " + " | ".join(str(row[col]) for col in columns) + " |\n"

            # Return the Markdown formatted results
            return md_table

    except pyodbc.Error as e:
        logging.error(f"Error executing query: {e}")
        raise


@mcp.tool(
    name="podbc_query_database",
    description="Execute a SQL query and return results in JSONL format."
)
def podbc_query_database(query: str, user:Optional[str]=None, password:Optional[str]=None, 
                    dsn:Optional[str]=None) -> str:
    """
    Execute a SQL query and return results in JSONL format.

    Args:
        query (str): The SQL query to execute.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in JSONL format.
    """
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            rs = cursor.execute(query)
            columns = [column[0] for column in rs.description]            
            results = []
            for row in rs:
                rs_dict = dict(zip(columns, row))
                truncated_row = {key: (str(value)[:MAX_LONG_DATA] if value is not None else None) for key, value in rs_dict.items()}
                results.append(truncated_row)                
                
            # Convert the results to JSONL format
            jsonl_results = "\n".join(json.dumps(row) for row in results)

            # Return the JSONL formatted results
            return jsonl_results
    except pyodbc.Error as e:
        logging.error(f"Error executing query: {e}")
        raise


@mcp.tool(
    name="podbc_spasql_query",
    description="Execute a SPASQL query and return results."
)
def podbc_spasql_query(query: str, max_rows:Optional[int] = 20, timeout:Optional[int] = 300000,
                    user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SPASQL query and return results in JSONL format.

    Args:
        query (str): The SPASQL query to execute.
        max_rows (int): Maximum number of rows to return. Default is 100.
        timeout (int): Query timeout. Default is 30000ms.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in requested format as string.
    """
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            cmd = f"select Demo.demo.execute_spasql_query(charset_recode(?, '_WIDE_', 'UTF-8'), ?, ?) as result"
            rs = cursor.execute(cmd, (query, max_rows, timeout,)).fetchone()
            return rs[0]
    except pyodbc.Error as e:
        logging.error(f"Error executing query: {e}")
        raise


@mcp.tool(
    name="podbc_virtuoso_support_ai",
    description="Tool to use the Virtuoso AI support function"
)
def podbc_virtuoso_support_ai(prompt: str, api_key:Optional[str]=None, user:Optional[str]=None, 
                            password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Tool to use the Virtuoso AI support function

    Args:
        prompt (str): AI prompt text (required).
        api_key (str): API key for AI service (optional).
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results data in JSON.
    """
    try:
        _api_key = api_key if api_key is not None else API_KEY
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            cmd = f"select DEMO.DBA.OAI_VIRTUOSO_SUPPORT_AI(?, ?) as result"
            rs = cursor.execute(cmd, (prompt, _api_key,)).fetchone()
            return rs[0]
    except pyodbc.Error as e:
        logging.error(f"Error executing request")
        raise pyodbc.Error("Error executing request")


@mcp.tool(
    name="podbc_sparql_func",
    description="Tool to use the SPARQL AI support function"
)
def podbc_sparql_func(prompt: str, api_key:Optional[str]=None, user:Optional[str]=None, 
                    password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Call SPARQL AI func.

    Args:
        prompt (str): The prompt.
        api_key (str): optional.
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results data in JSON.
    """
    try:
        _api_key = api_key if api_key is not None else API_KEY
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            cmd = f"select DEMO.DBA.OAI_SPARQL_FUNC(?, ?) as result"
            rs = cursor.execute(cmd, (prompt, _api_key,)).fetchone()
            return rs[0]
    except pyodbc.Error as e:
        logging.error(f"Error executing request")
        raise pyodbc.Error("Error executing request")


def _exec_sparql(query: str, format:Optional[str]="json", timeout:Optional[int]= 300000,
                 user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    timeout = 30000
    format = "json"
    try:
        with get_connection(True, user, password, dsn) as conn:
            cursor = conn.cursor()
            cmd = f"select Demo.demo.execute_spasql_query(charset_recode(?, '_WIDE_', 'UTF-8'), ?, ?) as result"
            rs = cursor.execute(cmd, (query, format, timeout,)).fetchone()
            return rs[0]
    except pyodbc.Error as e:
        logging.error(f"Error executing query: {e}")
        raise



@mcp.tool(
    name="podbc_sparql_get_entity_types",
    description="This query retrieves all entity types in the RDF graph, along with their labels and comments if available. "
                "It filters out blank nodes and ensures that only IRI types are returned. "
                "The LIMIT clause is set to 100 to restrict the number of entity types returned. "
)
def podbc_sparql_get_entity_types(user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SPARQL query and return results.

    Args:
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in requested format as string.
    """

    query = """
SELECT DISTINCT * FROM (
    SPARQL 
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    SELECT ?o 
    WHERE {
        GRAPH ?g {
            ?s a ?o .
            
            OPTIONAL {
                ?s rdfs:label ?label . 
                FILTER (LANG(?label) = "en" || LANG(?label) = "")
            }
            
            OPTIONAL {
                ?s rdfs:comment ?comment . 
                FILTER (LANG(?comment) = "en" || LANG(?comment) = "")
            }
            
            FILTER (isIRI(?o) && !isBlank(?o))
        }
    }
    LIMIT 100
) AS x 
    """
    return podbc_query_database(query, user=user, password=password, dsn=dsn)


@mcp.tool(
    name="podbc_sparql_get_entity_types_detailed",
    description="This query retrieves all entity types in the RDF graph, along with their labels and comments if available. "
                "It filters out blank nodes and ensures that only IRI types are returned. "
                "The LIMIT clause is set to 100 to restrict the number of entity types returned."
)
def podbc_sparql_get_entity_types_detailed(user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SPARQL query and return results.

    Args:
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in requested format as string.
    """

    query = """
SELECT * FROM (
    SPARQL
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 

    SELECT ?o, (SAMPLE(?label) AS ?label), (SAMPLE(?comment) AS ?comment)
    WHERE {
        GRAPH ?g {
            ?s a ?o .
            OPTIONAL {?o rdfs:label ?label . FILTER (LANG(?label) = "en" || LANG(?label) = "")}
            OPTIONAL {?o rdfs:comment ?comment . FILTER (LANG(?comment) = "en" || LANG(?comment) = "")}
            FILTER (isIRI(?o) && !isBlank(?o))
        }
    }
    GROUP BY ?o
    ORDER BY ?o
    LIMIT 20
) AS results 
    """
    return podbc_query_database(query, user=user, password=password, dsn=dsn)


@mcp.tool(
    name="podbc_sparql_get_entity_types_samples",
    description="This query retrieves samples of entities for each type in the RDF graph, along with their labels and counts. "
                "It groups by entity type and orders the results by sample count in descending order. "
                "Note: The LIMIT clause is set to 20 to restrict the number of entity types returned."
)
def podbc_sparql_get_entity_types_samples(user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SPARQL query and return results.

    Args:
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in requested format as string.
    """

    query = """
SELECT * FROM (
    SPARQL
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    SELECT (SAMPLE(?s) AS ?sample), ?slabel, (COUNT(*) AS ?sampleCount), (?o AS ?entityType), ?olabel
    WHERE {
        GRAPH ?g {
            ?s a ?o .
            OPTIONAL {?s rdfs:label ?slabel . FILTER (LANG(?slabel) = \"en\" || LANG(?slabel) = \"\")}
            FILTER (isIRI(?s) && !isBlank(?s))
            OPTIONAL {?o rdfs:label ?olabel . FILTER (LANG(?olabel) = \"en\" || LANG(?olabel) = \"\")}
            FILTER (isIRI(?o) && !isBlank(?o))
        }
    }
    GROUP BY ?slabel ?o ?olabel
    ORDER BY DESC(?sampleCount) ?o ?slabel ?olabel
    LIMIT 20
) AS results
    """
    return podbc_query_database(query, user=user, password=password, dsn=dsn)


@mcp.tool(
    name="podbc_sparql_get_ontologies",
    description="This query retrieves all ontologies in the RDF graph, along with their labels and comments if available."
)
def podbc_sparql_get_ontologies(user:Optional[str]=None, password:Optional[str]=None, dsn:Optional[str]=None) -> str:
    """
    Execute a SPARQL query and return results.

    Args:
        user (Optional[str]=None): Optional username.
        password (Optional[str]=None): Optional password.
        dsn (Optional[str]=None): Optional dsn name.

    Returns:
        str: Results in requested format as string.
    """

    query = """
SELECT * FROM (
    SPARQL 
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?s, ?label, ?comment 
    WHERE {
        GRAPH ?g {
            ?s a owl:Ontology .
            
            OPTIONAL {
                ?s rdfs:label ?label . 
                FILTER (LANG(?label) = "en" || LANG(?label) = "")
            }
            
            OPTIONAL {
                ?s rdfs:comment ?comment . 
                FILTER (LANG(?comment) = "en" || LANG(?comment) = "")
            }
            
            FILTER (isIRI(?o) && !isBlank(?o))
        }
    }
    LIMIT 100
) AS x
    """
    return podbc_query_database(query, user=user, password=password, dsn=dsn)



if __name__ == "__main__":
    mcp.run()
