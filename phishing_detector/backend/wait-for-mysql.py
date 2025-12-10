import time
import pymysql
import os
import sys

def wait_for_mysql():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            connection = pymysql.connect(
                host='mysql',
                user='phishing_user',
                password='phishing_pass',
                database='phishing_db'
            )
            connection.close()
            print("MySQL is ready!")
            return True
        except:
            retry_count += 1
            print(f"Waiting for MySQL... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    print("MySQL not ready after 60 seconds")
    return False

if __name__ == "__main__":
    if wait_for_mysql():
        sys.exit(0)
    else:
        sys.exit(1)