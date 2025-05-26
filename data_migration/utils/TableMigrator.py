import psycopg2
from psycopg2.extras import RealDictCursor

class TableMigrator:
    """A class to handle batch migration of tables from source to target."""
    
    def __init__(self, conn_config, batch_size=2000, total_limit=None, testing=False):
        """
        Initialize the migrator.
        
        Args:
            conn_config (dict): PostgreSQL connection configuration.
            batch_size (int): Number of records to process per batch.
        """
        self.conn_config = conn_config
        self.batch_size = batch_size
        self.total_migrated = 0
        self.total_limit = total_limit
        self.testing = testing
    
    def migrate_table(self, source_query, insert_query, source_params=None, validate_func=None, transform_func=None):
        """
        Migrate data from a source query to a target table in batches with validation before transformation.
        
        Args:
            source_query (str): SQL query to fetch records from the source table.
            insert_query (str): SQL query to insert records into the target table.
            source_params (tuple, optional): Parameters for the source query.
            transform_func (callable, optional): Function to transform source rows after validation.
            validate_func (callable, optional): Function to validate rows before transformation.
        
        Returns:
            int: Total number of records successfully migrated.
        """
        records_migrated = 0
        offset = 0

        if ";" in source_query:
            source_query = source_query.replace(";", "")
        
        try:
            with psycopg2.connect(**self.conn_config) as conn:
                while True:

                    if self.total_limit is not None and offset >= self.total_limit:
                        break

                    # Modify source query to include LIMIT and OFFSET
                    if self.total_limit is not None:
                        batch_limit = self.total_limit if self.batch_size > self.total_limit else self.batch_size
                        batch_limit = self.total_limit - offset if (self.batch_size + offset) > self.total_limit else self.batch_size
                    else:
                        batch_limit = self.batch_size

                    batch_query = f"{source_query} LIMIT %s OFFSET %s;"
                    batch_params = (source_params or ()) + (batch_limit, offset)

                    with conn.cursor(name=f"server_cursor_{offset}", cursor_factory=RealDictCursor) as server_cursor:
                        server_cursor.itersize = self.batch_size
                        server_cursor.execute(batch_query, batch_params)
                        
                        # batch = server_cursor.fetchall()  # Fetch all for this batch
                        batch = [dict(row) for row in server_cursor.fetchall()]  # Fetch all for this batch
                        
                        if not batch:
                            break
                            
                        with conn.cursor() as client_cursor:
                            # Validate rows first
                            if validate_func:
                                valid_batch = []
                                invalid_rows = []
                                for row in batch:
                                    try:
                                        if validate_func(row):
                                            valid_batch.append(row)
                                        else:
                                            invalid_rows.append(row)
                                    except Exception as e:
                                        invalid_rows.append((row, str(e)))
                                
                                if invalid_rows:
                                    print(f"Skipped {len(invalid_rows)} invalid rows: {invalid_rows}")
                                batch = valid_batch
                            
                            # Transform valid rows
                            if transform_func:
                                batch = [transform_func(row) for row in batch]
                            
                            # Insert valid and transformed rows
                            if batch and self.testing is not True:
                                client_cursor.executemany(insert_query, batch)
                        
                        records_migrated += len(batch)
                        offset += batch_limit
                        self.total_migrated += len(batch)
                        print(f"Migrated {len(batch)} records. Table total: {records_migrated}")
                        server_cursor.close()

            conn.commit() # Commit after the loop finishes
        
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback() # Rollback in case of error
            raise
        
        return records_migrated
    
    def get_total_migrated_count(self):
        return self.total_migrated

    def reset_migrate_counter(self):
        self.total_migrated = 0
