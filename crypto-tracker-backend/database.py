"""Database migration and management utilities."""
import json
import os
from datetime import datetime
from models import db, User, Transaction, PriceCache, PortfolioSnapshot

def create_tables():
    """Create all database tables."""
    db.create_all()
    print("✅ Database tables created successfully!")

def migrate_from_json():
    """Migrate existing JSON data to database."""
    print("🔄 Starting migration from JSON files to database...")
    
    # Create a default user for existing data
    default_user = User.query.filter_by(username='default').first()
    if not default_user:
        default_user = User(
            username='default',
            email='default@cryptotracker.local'
        )
        default_user.set_password('defaultpassword123')
        db.session.add(default_user)
        db.session.commit()
        print("✅ Created default user for migration")
    
    # Migrate manual transactions
    manual_tx_file = 'manual_transactions.json'
    if os.path.exists(manual_tx_file):
        try:
            with open(manual_tx_file, 'r') as f:
                transactions_data = json.load(f)
            
            for tx_data in transactions_data:
                # Check if transaction already exists
                existing_tx = Transaction.query.filter_by(
                    user_id=default_user.id,
                    coin=tx_data['coin'],
                    transaction_date=datetime.fromisoformat(tx_data['date'])
                ).first()
                
                if not existing_tx:
                    transaction = Transaction(
                        user_id=default_user.id,
                        coin=tx_data['coin'],
                        transaction_type=tx_data['type'],
                        amount=float(tx_data['amount']),
                        price_usd=float(tx_data['price']),
                        total_value_usd=float(tx_data['amount']) * float(tx_data['price']),
                        transaction_date=datetime.fromisoformat(tx_data['date'])
                    )
                    db.session.add(transaction)
            
            db.session.commit()
            print(f"✅ Migrated {len(transactions_data)} manual transactions")
            
        except Exception as e:
            print(f"❌ Error migrating manual transactions: {e}")
            db.session.rollback()
    
    # Migrate price cache
    price_cache_file = 'price_cache.json'
    if os.path.exists(price_cache_file):
        try:
            with open(price_cache_file, 'r') as f:
                price_data = json.load(f)
            
            migrated_prices = 0
            for date_str, prices in price_data.items():
                date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
                
                for coin, price in prices.items():
                    # Check if price already cached
                    existing_price = PriceCache.query.filter_by(
                        coin=coin,
                        date=date_obj
                    ).first()
                    
                    if not existing_price:
                        price_cache = PriceCache(
                            coin=coin,
                            date=date_obj,
                            price_usd=float(price)
                        )
                        db.session.add(price_cache)
                        migrated_prices += 1
            
            db.session.commit()
            print(f"✅ Migrated {migrated_prices} price cache entries")
            
        except Exception as e:
            print(f"❌ Error migrating price cache: {e}")
            db.session.rollback()
    
    print("✅ Migration completed successfully!")

def create_admin_user():
    """Create an admin user for the application."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@cryptotracker.local'
        )
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print("✅ Created admin user (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Change the admin password in production!")
    else:
        print("ℹ️  Admin user already exists")

def initialize_database():
    """Initialize database with tables and migration."""
    create_tables()
    migrate_from_json()
    create_admin_user()
    print("\n🎉 Database initialization completed!")
    print("📚 You can now use the new database-powered API endpoints")

if __name__ == '__main__':
    from app_enhanced import app
    with app.app_context():
        initialize_database()