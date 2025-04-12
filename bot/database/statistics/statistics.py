from typing import Optional, Dict, List, Tuple
from ..connect import get_db_connection

def get_url_statistics(url: str, detailed: bool = False) -> Dict:
    """
    Get statistics for a specific URL from the link_statistics table.
    
    Args:
        url: The URL to query statistics for
        detailed: If True, returns additional statistics like average processing time
                 If False, returns only the count of occurrences
    
    Returns:
        Dictionary containing statistics:
        - count: Number of times the URL was processed
        If detailed=True, also includes:
        - avg_processing_time: Average processing time for the URL
        - first_seen: Timestamp of first occurrence
        - last_seen: Timestamp of last occurrence
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if not detailed:
            # Simple count query
            cur.execute(
                "SELECT COUNT(*) FROM link_statistics WHERE url = %s",
                (url,)
            )
            count = cur.fetchone()[0]
            return {"count": count}
        else:
            # Detailed statistics query
            cur.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(processing_time) as avg_time,
                    MIN(created_at) as first_seen,
                    MAX(created_at) as last_seen
                FROM link_statistics 
                WHERE url = %s
                GROUP BY url
            """, (url,))
            
            result = cur.fetchone()
            if result:
                count, avg_time, first_seen, last_seen = result
                return {
                    "count": count,
                    "avg_processing_time": round(avg_time, 3),
                    "first_seen": first_seen,
                    "last_seen": last_seen
                }
            return {
                "count": 0,
                "avg_processing_time": 0,
                "first_seen": None,
                "last_seen": None
            }
            
    finally:
        cur.close()
        conn.close()