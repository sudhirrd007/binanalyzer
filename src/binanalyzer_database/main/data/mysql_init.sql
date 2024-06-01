USE binanalyzer_database;

-- Create binance_transactions table
CREATE TABLE IF NOT EXISTS binance_transactions (
    order_id VARCHAR(255) PRIMARY KEY,
    quote_id VARCHAR(255) NOT NULL,
    coin VARCHAR(255) NOT NULL,
    timezone VARCHAR(255),
    timestamp BIGINT,
    year INT,
    month INT,
    day INT,
    time VARCHAR(255),
    order_status VARCHAR(255) NOT NULL,
    automatically_added BOOLEAN,
    coin_amount DOUBLE NOT NULL,
    conversion_ratio DOUBLE NOT NULL,
    usdt_equivalent DOUBLE NOT NULL,
    trade_type VARCHAR(255) NOT NULL,
    buy_sell BOOLEAN,
    miscellaneous TEXT
);

-- Create spot_wallet table
CREATE TABLE IF NOT EXISTS spot_wallet (
    coin VARCHAR(255) PRIMARY KEY,
    free_coins DOUBLE NOT NULL,
    locked_coins DOUBLE NOT NULL,
    freeze_coins DOUBLE NOT NULL,
    withdrawing_coins DOUBLE NOT NULL,
    ipoable_coins DOUBLE NOT NULL,
    total_coins DOUBLE NOT NULL
);

-- Create trigger to calculate total_coins before insertion
-- CREATE TRIGGER before_insert_spot_wallet
-- BEFORE INSERT ON spot_wallet
-- FOR EACH ROW
-- BEGIN
--     SET NEW.total_coins = NEW.free_coins + NEW.locked_coins + NEW.freeze_coins + NEW.withdrawing_coins + NEW.ipoable_coins;
-- END;

-- Create funding_wallet table
CREATE TABLE IF NOT EXISTS funding_wallet (
    coin VARCHAR(255) PRIMARY KEY,
    free_coins DOUBLE NOT NULL,
    locked_coins DOUBLE NOT NULL,
    freeze_coins DOUBLE NOT NULL,
    withdrawing_coins DOUBLE NOT NULL,
    total_coins DOUBLE NOT NULL
);

-- Create trigger to calculate total_coins before insertion
-- CREATE TRIGGER before_insert_funding_wallet
-- BEFORE INSERT ON funding_wallet
-- FOR EACH ROW
-- BEGIN
--     SET NEW.total_coins = NEW.free_coins + NEW.locked_coins + NEW.freeze_coins + NEW.withdrawing_coins;
-- END;

-- Create earn_wallet table
CREATE TABLE IF NOT EXISTS earn_wallet (
    coin VARCHAR(255) PRIMARY KEY,
    total_coins DOUBLE NOT NULL
);
