CREATE TABLE banks (

    bank_id INTEGER PRIMARY KEY,

    bank_name VARCHAR(255) NOT NULL,

    app_name VARCHAR(255) NOT NULL

);

CREATE TABLE reviews (

    review_id VARCHAR(255) PRIMARY KEY,

    bank_id INTEGER REFERENCES banks(bank_id),

    review_text TEXT NOT NULL,

    rating INTEGER,

    review_date DATE,

    sentiment_label VARCHAR(50),

    sentiment_score FLOAT,

    identified_theme VARCHAR(255),

    source VARCHAR(100)

);