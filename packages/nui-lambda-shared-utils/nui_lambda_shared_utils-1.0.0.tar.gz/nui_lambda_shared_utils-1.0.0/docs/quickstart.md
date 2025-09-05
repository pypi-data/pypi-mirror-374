# Quick Start Guide

Get up and running with `nui-lambda-shared-utils` in minutes.

## Installation

```bash
# Install with all integrations
pip install nui-lambda-shared-utils[all]
```

## Basic Configuration

```python
import nui_lambda_shared_utils as nui

# Configure the package
nui.configure(
    es_host="your-elasticsearch:9200",
    es_credentials_secret="your-es-secret",
    db_credentials_secret="your-db-secret",
    slack_credentials_secret="your-slack-secret",
    aws_region="us-east-1"
)
```

## Common Usage Patterns

### 1. Simple Lambda Handler with Error Handling

```python
import nui_lambda_shared_utils as nui

# Configure once at module level
nui.configure(
    slack_credentials_secret="prod/slack-token",
    aws_region="us-east-1"
)

@nui.handle_lambda_error
@nui.with_retry(max_attempts=3)
def lambda_handler(event, context):
    """Lambda function with automatic error handling and retries."""
    slack = nui.SlackClient()
    
    # Process your data
    processed_count = len(event.get('records', []))
    
    # Send notification
    slack.send_message(
        channel="#alerts",
        text=f"Processed {processed_count} records successfully"
    )
    
    return {"statusCode": 200, "processed": processed_count}
```

### 2. Database Operations

```python
import nui_lambda_shared_utils as nui

# Configure database
nui.configure(db_credentials_secret="prod/database")

def get_user_data(user_id: int):
    """Get user data with connection pooling."""
    db = nui.DatabaseClient()
    
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            return cursor.fetchone()
```

### 3. Elasticsearch Search

```python
import nui_lambda_shared_utils as nui

# Configure Elasticsearch
nui.configure(
    es_host="your-cluster:9200",
    es_credentials_secret="prod/elasticsearch"
)

def search_logs(service: str, hours: int = 24):
    """Search application logs."""
    es = nui.ElasticsearchClient()
    
    # Use query builder for complex searches
    query = nui.ElasticsearchQueryBuilder()
    
    results = es.search(
        index=f"logs-{service}-*",
        body=query.time_range(hours=hours)
                  .match("level", "ERROR")
                  .build()
    )
    
    return results['hits']['hits']
```

### 4. Rich Slack Messages

```python
import nui_lambda_shared_utils as nui

def send_report(data: dict):
    """Send a formatted report to Slack."""
    slack = nui.SlackClient()
    builder = nui.SlackBlockBuilder()
    
    # Build rich message blocks
    blocks = (builder
        .add_header("Daily Report", emoji="📊")
        .add_context(f"Generated at {nui.format_nz_time()}")
        .add_divider()
        .add_fields([
            ("Total Records", nui.format_number(data['total'])),
            ("Processed", nui.format_number(data['processed'])),
            ("Success Rate", nui.format_percentage(data['success_rate']))
        ])
        .build()
    )
    
    slack.send_message(channel="#reports", blocks=blocks)
```

### 5. CloudWatch Metrics

```python
import nui_lambda_shared_utils as nui

def track_business_metrics(records_processed: int, processing_time: float):
    """Publish custom metrics to CloudWatch."""
    metrics = nui.MetricsPublisher(
        namespace="MyApplication",
        dimensions={"Environment": "production"}
    )
    
    # Publish metrics
    metrics.put_metric("RecordsProcessed", records_processed, unit="Count")
    metrics.put_metric("ProcessingTime", processing_time, unit="Milliseconds")
    
    # Metrics are automatically flushed when the object is destroyed
    # Or manually flush with: metrics.flush()
```

### 6. Complete Lambda Function Example

```python
import os
import nui_lambda_shared_utils as nui

# Configure once at module level
nui.configure(
    es_host=os.environ.get('ES_HOST'),
    es_credentials_secret=f"{os.environ.get('STAGE', 'dev')}/elasticsearch",
    db_credentials_secret=f"{os.environ.get('STAGE', 'dev')}/database",
    slack_credentials_secret=f"{os.environ.get('STAGE', 'dev')}/slack",
    aws_region=os.environ.get('AWS_REGION', 'us-east-1')
)

@nui.track_lambda_performance()
@nui.handle_lambda_error
def lambda_handler(event, context):
    """Complete example with all integrations."""
    
    # Initialize clients
    db = nui.DatabaseClient()
    es = nui.ElasticsearchClient()
    slack = nui.SlackClient()
    metrics = nui.MetricsPublisher("MyService")
    
    try:
        # Process records
        records = event.get('records', [])
        processed = 0
        
        for record in records:
            # Database operation
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO processed_records (data) VALUES (%s)",
                        (record,)
                    )
            
            processed += 1
        
        # Log to Elasticsearch
        es.index_document(
            index="application-logs",
            body={
                "timestamp": nui.get_nz_time(),
                "level": "INFO",
                "message": f"Processed {processed} records",
                "function_name": context.function_name
            }
        )
        
        # Send notification
        slack.send_message(
            channel="#notifications",
            text=f"Successfully processed {processed} records"
        )
        
        # Custom metrics
        metrics.put_metric("RecordsProcessed", processed, unit="Count")
        
        return {
            "statusCode": 200,
            "body": f"Processed {processed} records"
        }
        
    except Exception as e:
        # Error handling is automatic with decorators
        # Additional custom error handling can go here
        raise
```

## Next Steps

1. **Read the Configuration Guide** - [configuration.md](configuration.md) for detailed setup
2. **Explore Components** - Check individual component docs for advanced usage
3. **Set up AWS Resources** - Review [aws-infrastructure.md](aws-infrastructure.md) for required resources
4. **Testing** - See [testing.md](testing.md) for testing strategies

## Common Patterns

### Environment-Based Configuration
```python
import os
import nui_lambda_shared_utils as nui

stage = os.environ.get('STAGE', 'dev')

nui.configure(
    es_credentials_secret=f"{stage}/elasticsearch",
    db_credentials_secret=f"{stage}/database",
    slack_credentials_secret=f"{stage}/slack"
)
```

### Error Notifications
```python
@nui.handle_lambda_error
def lambda_handler(event, context):
    try:
        # Your logic here
        pass
    except Exception as e:
        # Send error notification
        slack = nui.SlackClient()
        slack.send_message(
            channel="#alerts",
            text=f"❌ Lambda error in {context.function_name}: {str(e)}"
        )
        raise  # Re-raise for proper Lambda error handling
```

### Retry with Backoff
```python
@nui.with_retry(max_attempts=3, backoff_factor=2)
def external_api_call():
    """Call with exponential backoff retry."""
    # API call logic here
    pass
```

This quick start should get you productive with the package immediately. For detailed documentation on each component, see the specific guides linked in the main documentation.