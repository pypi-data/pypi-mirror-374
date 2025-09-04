Database Security Tutorial
===========================

Learn how to secure databases with quantum-safe encryption using Sudarshan Engine.

.. contents::
   :local:
   :depth: 2

Overview
========

Database security is critical for protecting sensitive data. This tutorial shows how to integrate Sudarshan Engine with popular databases (PostgreSQL, MySQL, MongoDB) for quantum-safe data protection.

**What You'll Learn:**
- Encrypt database backups with quantum-safe algorithms
- Secure sensitive data at rest and in transit
- Implement field-level encryption
- Create secure database migration workflows

Prerequisites
=============

- Sudarshan Engine installed
- Database server (PostgreSQL, MySQL, MongoDB)
- Database client tools
- Basic SQL knowledge

.. code-block:: bash

   # Verify installation
   sudarshan --version

   # Check available algorithms
   python -c "from sudarshan.crypto import QuantumSafeCrypto; print('✅ Ready')"

Database Backup Encryption
==========================

**PostgreSQL Backup Security:**

.. code-block:: bash

   # Create PostgreSQL dump
   pg_dump mydatabase > database_backup.sql

   # Encrypt with Sudarshan Engine
   sudarshan spq_create \
       --input database_backup.sql \
       --output database_backup.spq \
       --password "DatabaseMasterKey2025!" \
       --algorithm kyber1024 \
       --signature dilithium5 \
       --compress

**MySQL Backup Security:**

.. code-block:: bash

   # Create MySQL dump
   mysqldump -u root -p mydatabase > mysql_backup.sql

   # Encrypt backup
   sudarshan spq_create \
       --input mysql_backup.sql \
       --output mysql_backup.spq \
       --password "MySQLSecureBackup!" \
       --compress

**MongoDB Backup Security:**

.. code-block:: bash

   # Create MongoDB backup
   mongodump --db mydatabase --out /tmp/mongodb_backup

   # Archive and encrypt
   tar -czf mongodb_backup.tar.gz /tmp/mongodb_backup
   sudarshan spq_create \
       --input mongodb_backup.tar.gz \
       --output mongodb_backup.spq \
       --password "MongoDBBackupKey!" \
       --algorithm kyber1024

Sensitive Data Protection
=========================

**Field-Level Encryption:**

.. code-block:: python

   from sudarshan import spq_create
   import json

   # Sensitive customer data
   sensitive_data = {
       "customers": [
           {
               "id": 1,
               "name": "John Doe",
               "ssn": "123-45-6789",  # Highly sensitive
               "credit_card": "4111111111111111",  # PCI DSS
               "medical_history": "Patient has diabetes"  # HIPAA
           }
       ]
   }

   # Encrypt sensitive fields individually
   encrypted_fields = {}
   for field in ['ssn', 'credit_card', 'medical_history']:
       field_data = sensitive_data['customers'][0][field].encode()
       metadata = {
           "field_name": field,
           "table": "customers",
           "record_id": 1,
           "encryption_level": "field_level",
           "compliance": ["PCI_DSS", "HIPAA"] if field in ['credit_card', 'medical_history'] else []
       }

       result = spq_create(
           filepath=f"field_{field}_customer_1.spq",
           metadata=metadata,
           payload=field_data,
           password=f"FieldPassword_{field}_2025!",
           algorithm="kyber1024"
       )
       encrypted_fields[field] = result['filepath']

   print(f"✅ Encrypted {len(encrypted_fields)} sensitive fields")

**PII Data Protection:**

.. code-block:: python

   import pandas as pd
   from sudarshan import spq_create

   # Load customer PII data
   df = pd.read_csv('customer_pii.csv')

   # Encrypt entire PII dataset
   pii_data = df.to_json(orient='records')

   metadata = {
       "data_type": "pii_dataset",
       "record_count": len(df),
       "fields": list(df.columns),
       "compliance": ["GDPR", "CCPA"],
       "retention_policy": "7_years",
       "access_level": "restricted"
   }

   result = spq_create(
       filepath="customer_pii_dataset.spq",
       metadata=metadata,
       payload=pii_data.encode(),
       password="PIIDatasetMasterKey2025!",
       compress=True,
       algorithm="kyber1024"
   )

Database Migration Security
===========================

**Secure Schema Migration:**

.. code-block:: python

   from sudarshan.protocols import TransactionCapsule
   import json

   # Database migration script
   migration = {
       "version": "1.2.0",
       "description": "Add PII encryption fields",
       "sql_commands": [
           "ALTER TABLE customers ADD COLUMN encrypted_ssn TEXT;",
           "ALTER TABLE customers ADD COLUMN encrypted_credit_card TEXT;",
           "CREATE INDEX idx_encrypted_ssn ON customers(encrypted_ssn);"
       ],
       "rollback_commands": [
           "ALTER TABLE customers DROP COLUMN encrypted_ssn;",
           "ALTER TABLE customers DROP COLUMN encrypted_credit_card;"
       ],
       "checksum": "sha256_hash_of_migration"
   }

   # Create migration capsule
   tx_capsule = TransactionCapsule()
   capsule = tx_capsule.create_migration_capsule(
       migration_data=migration,
       security_level="high"
   )

   # Encrypt migration
   metadata = {
       "migration_type": "schema_change",
       "database_version": "1.1.0 -> 1.2.0",
       "rollback_available": True,
       "test_environment_required": True
   }

   result = spq_create(
       filepath="database_migration.spq",
       metadata=metadata,
       payload=json.dumps(capsule).encode(),
       password="MigrationMasterKey2025!",
       compress=True
   )

**Data Migration with Encryption:**

.. code-block:: python

   # Migrate existing data with encryption
   def migrate_customer_data(customer_id, old_data):
       """Migrate customer data with field-level encryption"""

       # Extract sensitive fields
       sensitive_fields = {
           'ssn': old_data.get('ssn'),
           'credit_card': old_data.get('credit_card'),
           'bank_account': old_data.get('bank_account')
       }

       encrypted_fields = {}

       # Encrypt each sensitive field
       for field_name, field_value in sensitive_fields.items():
           if field_value:
               metadata = {
                   "migration_type": "data_encryption",
                   "field_name": field_name,
                   "customer_id": customer_id,
                   "original_length": len(str(field_value)),
                   "encryption_timestamp": "2025-09-02T11:31:13Z"
               }

               result = spq_create(
                   filepath=f"migrated_{field_name}_customer_{customer_id}.spq",
                   metadata=metadata,
                   payload=str(field_value).encode(),
                   password=f"MigrationKey_{field_name}_{customer_id}!",
                   algorithm="kyber1024"
               )

               encrypted_fields[field_name] = {
                   "encrypted_file": result['filepath'],
                   "encryption_method": "kyber1024",
                   "key_reference": f"key_{field_name}_{customer_id}"
               }

       # Update database with encrypted field references
       update_query = f"""
       UPDATE customers
       SET encrypted_ssn = '{encrypted_fields.get('ssn', {}).get('encrypted_file', '')}',
           encrypted_credit_card = '{encrypted_fields.get('credit_card', {}).get('encrypted_file', '')}',
           encrypted_bank_account = '{encrypted_fields.get('bank_account', {}).get('encrypted_file', '')}',
           migration_completed = true,
           migration_timestamp = NOW()
       WHERE id = {customer_id}
       """

       return {
           "customer_id": customer_id,
           "encrypted_fields": encrypted_fields,
           "migration_status": "completed",
           "update_query": update_query
       }

Audit Trail Protection
======================

**Database Audit Log Encryption:**

.. code-block:: python

   import logging
   from sudarshan import spq_create
   import json

   class SecureAuditLogger:
       def __init__(self, log_file="audit_log.spq"):
           self.log_file = log_file
           self.audit_entries = []

       def log_audit_event(self, event_data):
           """Log audit event with quantum-safe encryption"""

           audit_entry = {
               "timestamp": "2025-09-02T11:31:13Z",
               "event_type": event_data['type'],
               "user_id": event_data['user_id'],
               "action": event_data['action'],
               "resource": event_data['resource'],
               "ip_address": event_data.get('ip_address'),
               "user_agent": event_data.get('user_agent'),
               "success": event_data.get('success', True),
               "details": event_data.get('details', {})
           }

           self.audit_entries.append(audit_entry)

           # Encrypt audit log periodically (every 100 entries)
           if len(self.audit_entries) >= 100:
               self._encrypt_audit_batch()

       def _encrypt_audit_batch(self):
           """Encrypt batch of audit entries"""

           batch_data = {
               "audit_batch": self.audit_entries,
               "batch_size": len(self.audit_entries),
               "start_timestamp": self.audit_entries[0]['timestamp'],
               "end_timestamp": self.audit_entries[-1]['timestamp'],
               "batch_hash": self._calculate_batch_hash()
           }

           metadata = {
               "log_type": "database_audit",
               "batch_size": len(self.audit_entries),
               "retention_period": "7_years",
               "compliance": ["SOX", "GDPR"],
               "encryption_level": "maximum"
           }

           # Create timestamped audit log file
           timestamp = self.audit_entries[0]['timestamp'].replace(':', '-')
           audit_file = f"audit_log_{timestamp}.spq"

           result = spq_create(
               filepath=audit_file,
               metadata=metadata,
               payload=json.dumps(batch_data).encode(),
               password="AuditLogMasterKey2025!",
               compress=True,
               algorithm="kyber1024"
           )

           # Clear processed entries
           self.audit_entries.clear()

           return result

       def _calculate_batch_hash(self):
           """Calculate hash of audit batch for integrity"""
           import hashlib
           batch_content = json.dumps(self.audit_entries, sort_keys=True)
           return hashlib.sha256(batch_content.encode()).hexdigest()

   # Usage example
   audit_logger = SecureAuditLogger()

   # Log database access
   audit_logger.log_audit_event({
       "type": "database_access",
       "user_id": "admin_user",
       "action": "SELECT",
       "resource": "customers.ssn",
       "ip_address": "192.168.1.100",
       "success": True
   })

Multi-Database Support
=======================

**PostgreSQL Integration:**

.. code-block:: python

   import psycopg2
   from sudarshan import spq_create

   def secure_postgres_backup(connection_string, password):
       """Create secure PostgreSQL backup"""

       conn = psycopg2.connect(connection_string)
       cursor = conn.cursor()

       # Get database metadata
       cursor.execute("""
           SELECT schemaname, tablename, tableowner
           FROM pg_tables
           WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
           ORDER BY schemaname, tablename;
       """)

       tables = cursor.fetchall()

       # Create backup data structure
       backup_data = {
           "database_type": "postgresql",
           "tables": [],
           "backup_timestamp": "2025-09-02T11:31:13Z",
           "table_count": len(tables)
       }

       for schema, table, owner in tables:
           table_info = {
               "schema": schema,
               "name": table,
               "owner": owner,
               "row_count": 0,
               "sensitive_fields": []
           }

           # Get row count
           cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
           table_info["row_count"] = cursor.fetchone()[0]

           # Identify sensitive fields (simplified)
           cursor.execute(f"""
               SELECT column_name, data_type
               FROM information_schema.columns
               WHERE table_schema = %s AND table_name = %s
               AND column_name LIKE '%%password%%' OR column_name LIKE '%%ssn%%'
           """, (schema, table))

           sensitive_fields = cursor.fetchall()
           table_info["sensitive_fields"] = [
               {"name": col, "type": dtype} for col, dtype in sensitive_fields
           ]

           backup_data["tables"].append(table_info)

       conn.close()

       # Encrypt backup metadata
       metadata = {
           "backup_type": "postgresql_schema",
           "database_name": "production_db",
           "table_count": len(tables),
           "contains_sensitive_data": True,
           "compliance_required": ["GDPR", "HIPAA"]
       }

       result = spq_create(
           filepath="postgres_backup_metadata.spq",
           metadata=metadata,
           payload=json.dumps(backup_data).encode(),
           password=password,
           compress=True
       )

       return result

**MongoDB Integration:**

.. code-block:: python

   from pymongo import MongoClient
   from sudarshan import spq_create

   def secure_mongodb_backup(mongo_uri, database_name, password):
       """Create secure MongoDB backup"""

       client = MongoClient(mongo_uri)
       db = client[database_name]

       # Get collection statistics
       collections = db.list_collection_names()
       backup_metadata = {
           "database_type": "mongodb",
           "database_name": database_name,
           "collections": [],
           "backup_timestamp": "2025-09-02T11:31:13Z"
       }

       for collection_name in collections:
           collection = db[collection_name]

           # Get collection stats
           stats = db.command("collStats", collection_name)

           collection_info = {
               "name": collection_name,
               "document_count": stats.get("count", 0),
               "size_bytes": stats.get("size", 0),
               "storage_size_bytes": stats.get("storageSize", 0),
               "indexes": stats.get("nindexes", 0),
               "sensitive_fields": []
           }

           # Sample document to identify sensitive fields
           sample_doc = collection.find_one()
           if sample_doc:
               sensitive_patterns = ['password', 'ssn', 'credit_card', 'medical']
               for field in sample_doc.keys():
                   if any(pattern in field.lower() for pattern in sensitive_patterns):
                       collection_info["sensitive_fields"].append(field)

           backup_metadata["collections"].append(collection_info)

       client.close()

       # Encrypt backup metadata
       metadata = {
           "backup_type": "mongodb_schema",
           "database_name": database_name,
           "collection_count": len(collections),
           "total_documents": sum(c["document_count"] for c in backup_metadata["collections"]),
           "contains_pii": any(c["sensitive_fields"] for c in backup_metadata["collections"])
       }

       result = spq_create(
           filepath="mongodb_backup_metadata.spq",
           metadata=metadata,
           payload=json.dumps(backup_metadata).encode(),
           password=password,
           compress=True
       )

       return result

Compliance and Regulatory Requirements
======================================

**GDPR Compliance:**

.. code-block:: python

   from sudarshan.protocols import InnerShield

   def gdpr_compliant_data_processing(user_data):
       """Process user data with GDPR compliance"""

       shield = InnerShield()

       # Encrypt PII data
       encrypted_pii = shield.wrap_pii_data(
           user_data=user_data,
           consent_timestamp="2025-09-02T11:31:13Z",
           retention_period="2_years",
           legal_basis="consent"
       )

       # Create audit trail
       audit_entry = {
           "event": "data_processing",
           "user_id": user_data['id'],
           "processing_type": "encryption",
           "gdpr_compliant": True,
           "consent_obtained": True,
           "timestamp": "2025-09-02T11:31:13Z"
       }

       # Encrypt audit entry
       metadata = {
           "compliance": "GDPR",
           "data_subject_rights": ["access", "rectification", "erasure"],
           "retention_schedule": "2_years",
           "audit_trail": True
       }

       result = spq_create(
           filepath=f"gdpr_audit_user_{user_data['id']}.spq",
           metadata=metadata,
           payload=json.dumps(audit_entry).encode(),
           password="GDPRComplianceKey2025!",
           algorithm="kyber1024"
       )

       return {
           "encrypted_data": encrypted_pii,
           "audit_record": result,
           "compliance_status": "gdpr_compliant"
       }

**HIPAA Compliance:**

.. code-block:: python

   def hipaa_compliant_medical_data(medical_record):
       """Process medical data with HIPAA compliance"""

       # Encrypt PHI (Protected Health Information)
       phi_fields = ['diagnosis', 'treatment', 'medication', 'test_results']

       encrypted_record = medical_record.copy()

       for field in phi_fields:
           if field in medical_record:
               field_data = str(medical_record[field]).encode()

               metadata = {
                   "compliance": "HIPAA",
                   "data_type": "protected_health_information",
                   "field_name": field,
                   "patient_id": medical_record.get('patient_id'),
                   "encryption_timestamp": "2025-09-02T11:31:13Z",
                   "access_controls": ["medical_staff_only", "audit_required"]
               }

               result = spq_create(
                   filepath=f"hipaa_{field}_patient_{medical_record['patient_id']}.spq",
                   metadata=metadata,
                   payload=field_data,
                   password="HIPAAComplianceKey2025!",
                   algorithm="kyber1024"
               )

               encrypted_record[field] = {
                   "encrypted": True,
                   "file_reference": result['filepath'],
                   "encryption_method": "kyber1024"
               }

       return encrypted_record

Performance Optimization
========================

**Batch Processing:**

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor
   from sudarshan import spq_create

   def batch_encrypt_database_records(records, password):
       """Batch encrypt multiple database records"""

       def encrypt_record(record):
           metadata = {
               "record_type": "database_row",
               "table_name": record['table'],
               "primary_key": record['id'],
               "batch_processing": True
           }

           return spq_create(
               filepath=f"record_{record['table']}_{record['id']}.spq",
               metadata=metadata,
               payload=json.dumps(record).encode(),
               password=password,
               compress=True
           )

       # Process in parallel
       with ThreadPoolExecutor(max_workers=4) as executor:
           results = list(executor.map(encrypt_record, records))

       return results

**Streaming Encryption for Large Datasets:**

.. code-block:: python

   import io
   from sudarshan import spq_create

   def stream_encrypt_large_dataset(dataset_file, password, chunk_size=1024*1024):
       """Stream encrypt large dataset in chunks"""

       encrypted_chunks = []

       with open(dataset_file, 'rb') as f:
           chunk_number = 0
           while True:
               chunk = f.read(chunk_size)
               if not chunk:
                   break

               # Encrypt chunk
               metadata = {
                   "chunk_number": chunk_number,
                   "chunk_size": len(chunk),
                   "total_file": dataset_file,
                   "streaming_encryption": True
               }

               result = spq_create(
                   filepath=f"chunk_{chunk_number:06d}.spq",
                   metadata=metadata,
                   payload=chunk,
                   password=password,
                   compress=False  # Chunks are already compressed if needed
               )

               encrypted_chunks.append(result)
               chunk_number += 1

       # Create manifest file
       manifest = {
           "original_file": dataset_file,
           "total_chunks": len(encrypted_chunks),
           "chunk_size": chunk_size,
           "total_size": sum(r['file_size'] for r in encrypted_chunks),
           "encryption_timestamp": "2025-09-02T11:31:13Z"
       }

       manifest_result = spq_create(
           filepath="dataset_manifest.spq",
           metadata={"type": "streaming_manifest"},
           payload=json.dumps(manifest).encode(),
           password=password
       )

       return {
           "manifest": manifest_result,
           "chunks": encrypted_chunks,
           "total_chunks": len(encrypted_chunks)
       }

Monitoring and Alerting
========================

**Database Security Monitoring:**

.. code-block:: python

   from sudarshan.security import SecurityMonitor

   class DatabaseSecurityMonitor:
       def __init__(self):
           self.monitor = SecurityMonitor()
           self.alerts = []

       def monitor_database_access(self, access_event):
           """Monitor database access patterns"""

           # Analyze access pattern
           risk_score = self._calculate_risk_score(access_event)

           if risk_score > 0.7:  # High risk
               alert = {
                   "type": "high_risk_access",
                   "user": access_event['user'],
                   "query": access_event['query'],
                   "risk_score": risk_score,
                   "timestamp": "2025-09-02T11:31:13Z"
               }

               self.alerts.append(alert)

               # Encrypt alert for secure storage
               metadata = {
                   "alert_type": "security_incident",
                   "severity": "high",
                   "requires_investigation": True
               }

               spq_create(
                   filepath=f"security_alert_{len(self.alerts)}.spq",
                   metadata=metadata,
                   payload=json.dumps(alert).encode(),
                   password="SecurityAlertKey2025!"
               )

       def _calculate_risk_score(self, access_event):
           """Calculate risk score for access event"""
           score = 0.0

           # High-risk queries
           if 'DROP' in access_event['query'].upper():
               score += 0.5
           if 'DELETE' in access_event['query'].upper():
               score += 0.3

           # Unusual access patterns
           if access_event.get('unusual_time', False):
               score += 0.2
           if access_event.get('unusual_location', False):
               score += 0.2

           return min(score, 1.0)

Next Steps
==========

- **Payment System Integration**: :doc:`payment_system`
- **Custom Protocol Development**: :doc:`custom_protocols`
- **API Integration**: :doc:`../guides/api_integration`

.. tip::
   For large databases, consider using streaming encryption to handle memory constraints efficiently.

.. warning::
   Always backup encryption keys separately from encrypted data. Use different passwords for different datasets.

.. note::
   Database encryption with Sudarshan Engine provides quantum-resistant protection for both data at rest and in transit.