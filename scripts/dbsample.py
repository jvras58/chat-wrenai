import random
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from utils.settings import settings


class SampleDB:
    def __init__(self):
        self.engine = create_async_engine(settings.sample_db_url, echo=True)
        self.SessionLocal = async_sessionmaker(bind=self.engine)
    
    async def create_sample_db(self):
        """Cria schema + 10k linhas de dados BI realistas"""
        async with self.engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS sales;"))
            await conn.execute(text("DROP TABLE IF EXISTS products;"))
            await conn.execute(text("DROP TABLE IF EXISTS regions;"))
            
            await conn.execute(text("""
                CREATE TABLE regions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50),
                    manager VARCHAR(100)
                );
            """))
            
            await conn.execute(text("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100),
                    category VARCHAR(50),
                    price DECIMAL(10,2)
                );
            """))
            
            await conn.execute(text("""
                CREATE TABLE sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region_id INTEGER REFERENCES regions(id),
                    product_id INTEGER REFERENCES products(id),
                    sale_date DATE,
                    quantity INTEGER,
                    total DECIMAL(12,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            await conn.execute(text("""
                INSERT INTO regions (name, manager) VALUES
                ('Sudeste', 'Maria Silva'),
                ('Nordeste', 'João Santos'),
                ('Sul', 'Ana Costa'),
                ('Norte', 'Pedro Lima'),
                ('Centro-Oeste', 'Carla Souza');
            """))
            
            await conn.execute(text("""
                INSERT INTO products (name, category, price) VALUES
                ('Notebook Pro', 'Eletrônicos', 4500.00),
                ('Smartphone X', 'Eletrônicos', 2500.00),
                ('Mesa Gamer', 'Móveis', 1200.00),
                ('Cadeira Ergo', 'Móveis', 800.00),
                ('Monitor 4K', 'Eletrônicos', 1800.00);
            """))
            
            print("Gerando 10k vendas...")
            sales_data = []
            regions = list(range(1, 6))
            products = list(range(1, 6))
            
            base_date = datetime(2024, 1, 1)
            for i in range(10000):
                region_id = random.choice(regions)
                product_id = random.choice(products)
                qty = random.randint(1, 10)
                date_offset = timedelta(days=random.randint(0, 730))
                
                sales_data.append({
                    "region_id": region_id,
                    "product_id": product_id,
                    "sale_date": (base_date + date_offset).date(),
                    "quantity": qty,
                    "total": qty * random.uniform(0.9, 1.1) * 100
                })
            
            await conn.execute(text("""
                INSERT INTO sales (region_id, product_id, sale_date, quantity, total)
                VALUES (:region_id, :product_id, :sale_date, :quantity, :total)
            """), sales_data)
            
            await conn.commit()
            print("✅ Banco de exemplo criado! 10k vendas + schema BI")

if __name__ == "__main__":
    import asyncio

    async def main():
        db_sample = SampleDB()
        await db_sample.create_sample_db()

    asyncio.run(main())
