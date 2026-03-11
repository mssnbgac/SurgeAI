.PHONY: install compile test deploy-local deploy-testnet start-backend start-frontend start-agent

install:
	@echo "Installing dependencies..."
	npm install
	cd frontend && npm install
	cd backend && npm install
	cd agent && pip install -r requirements.txt

compile:
	@echo "Compiling contracts..."
	npx hardhat compile

test:
	@echo "Running tests..."
	npx hardhat test

deploy-local:
	@echo "Deploying to local network..."
	npx hardhat run scripts/deploy.ts --network localhost

deploy-testnet:
	@echo "Deploying to Base Sepolia..."
	npx hardhat run scripts/deploy.ts --network baseSepolia

start-backend:
	@echo "Starting backend server..."
	cd backend && npm run dev

start-frontend:
	@echo "Starting frontend..."
	cd frontend && npm run dev

start-agent:
	@echo "Starting AI agent..."
	cd agent && python main.py

dev:
	@echo "Starting all services..."
	@echo "Run these in separate terminals:"
	@echo "  make start-backend"
	@echo "  make start-frontend"
	@echo "  make start-agent"
