-- Create binance_transactions table
CREATE TABLE IF NOT EXISTS binance_transactions (
    order_id TEXT PRIMARY KEY,
    quote_id TEXT NOT NULL,
    coin TEXT NOT NULL,
    timezone TEXT,
    timestamp INTEGER,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    time TEXT,
    order_status TEXT NOT NULL,
    automatically_added INTEGER CHECK (automatically_added IN (0, 1)),
    coin_amount REAL NOT NULL,
    conversion_ratio REAL NOT NULL,
    usdt_equivalent REAL NOT NULL,
    trade_type TEXT NOT NULL,
    buy_sell TEXT INTEGER CHECK (automatically_added IN (0, 1)),
    miscellaneous TEXT
);

-- Create spot_wallet table
CREATE TABLE IF NOT EXISTS spot_wallet (
    coin TEXT PRIMARY KEY COLLATE NOCASE,
    free_coins REAL NOT NULL,
    locked_coins REAL NOT NULL,
    freeze_coins REAL NOT NULL,
    withdrawing_coins REAL NOT NULL,
    ipoable_coins REAL NOT NULL,
    total_coins REAL NOT NULL
);

-- Create trigger to calculate total_coins before insertion
CREATE TRIGGER IF NOT EXISTS before_insert_spot_wallet
BEFORE INSERT ON spot_wallet
FOR EACH ROW
BEGIN
    SELECT NEW.total_coins = NEW.free_coins + NEW.locked_coins + NEW.freeze_coins + NEW.withdrawing_coins + NEW.ipoable_coins;
END;

-- Create spot_wallet table
CREATE TABLE IF NOT EXISTS spot_wallet (
    coin TEXT PRIMARY KEY COLLATE NOCASE,
    free_coins REAL NOT NULL,
    locked_coins REAL NOT NULL,
    freeze_coins REAL NOT NULL,
    withdrawing_coins REAL NOT NULL,
    ipoable_coins REAL NOT NULL,
    total_coins REAL NOT NULL
);

-- Create trigger to calculate total_coins before insertion
CREATE TRIGGER IF NOT EXISTS before_insert_spot_wallet
BEFORE INSERT ON spot_wallet
FOR EACH ROW
BEGIN
    SELECT NEW.total_coins = NEW.free_coins + NEW.locked_coins + NEW.freeze_coins + NEW.withdrawing_coins + NEW.ipoable_coins;
END;

-- Create funding_wallet table
CREATE TABLE IF NOT EXISTS funding_wallet (
    coin TEXT PRIMARY KEY COLLATE NOCASE,
    free_coins REAL NOT NULL,
    locked_coins REAL NOT NULL,
    freeze_coins REAL NOT NULL,
    withdrawing_coins REAL NOT NULL,
    total_coins REAL NOT NULL
);

-- Create trigger to calculate total_coins before insertion
CREATE TRIGGER IF NOT EXISTS before_insert_funding_wallet
BEFORE INSERT ON funding_wallet
FOR EACH ROW
BEGIN
    SELECT NEW.total_coins = NEW.free_coins + NEW.locked_coins + NEW.freeze_coins + NEW.withdrawing_coins;
END;

-- Create earn_wallet table
CREATE TABLE IF NOT EXISTS earn_wallet (
    coin TEXT PRIMARY KEY COLLATE NOCASE,
    total_coins REAL NOT NULL
);
