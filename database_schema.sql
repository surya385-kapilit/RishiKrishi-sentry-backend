-- ========== SUPERADMIN TABLE ==========
CREATE TABLE superadmins (
    superadmin_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    full_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== TENANTS TABLE ==========
CREATE TABLE tenants (
    tenant_id VARCHAR(12) PRIMARY KEY,
    tenant_name VARCHAR(255) NOT NULL,
    tenant_domain VARCHAR(255) UNIQUE NOT NULL,
    schema_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== MATRIX (USERS) TABLE ==========
CREATE TABLE matrix (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(12) NOT NULL,
    tenant_id VARCHAR(12) NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) ,
    phone_no VARCHAR(15) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== Subscription Table ==========


CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR(12) NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'premium', 'enterprise')),
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'expired', 'cancelled')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stripe_subscription_id TEXT
);



-- ========== INDEXES ==========
-- Indexes for matrix (users)
CREATE INDEX idx_matrix_tenant_id ON matrix(tenant_id);
CREATE INDEX idx_matrix_email ON matrix(email);

-- Index for superadmin
CREATE INDEX idx_superadmins_email ON superadmins(email);

-- Index for tenants
CREATE INDEX idx_tenants_domain ON tenants(tenant_domain);


-- Index for subscriptions
CREATE INDEX idx_subscriptions_tenant_id ON subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);


