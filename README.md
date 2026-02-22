
## Local Development

### Prerequisites

- Python 3.10+
- uv (optional, but recommended)

### Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your database credentials.

3. **Run the app:**
   ```bash
   .venv\Scripts\project.exe
   ```

   Or activate the environment first:
   ```bash
   .venv\Scripts\activate
   project
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

# **Project Proposal – Rental Payment Management System**

## **Proposed Software Name**

**RentTrack**

## **Purpose of the Software**

RentTrack is a software application designed to support basic rental management for landlords. The purpose of the system is to store and manage information related to rental properties, tenants, and rent payments, and to track rental arrears over time. The software provides simple reporting functionality to help users identify overdue payments and review payment history.

**Target Audience**

The target audience for RentTrack is small-scale residential landlords who manage less than 2 rental units to track rent payments, and outstanding balances. The software is intended for administrative use rather than for tenants.

## **Functionalities**

- Create, view, update, and delete rental property records  
- Record rent payments made by tenants  
- Automatically calculate and track rental arrears based on expected rent and payments received  
- The application will be usable through a basic command-line interface.

## **Opportunities for using design patterns** 

* Factory Pattern:  
  * To create objects such as properties, and payment records while encapsulating object creation logic within the factory.   
* State pattern (not discussed in class) \- documentation: [https://refactoring.guru/design-patterns/state](https://refactoring.guru/design-patterns/state#:~:text=State%20is%20a%20behavioral%20design,the%20object%20changed%20its%20class)   
  * This design pattern can be used here to track the rental payment state change from Charged, Paid, Late, and In Arrears. 

## **Intended Technologies**

* **Programming Language:** Python  
  * Used to implement application logic, design patterns, and overall system behavior  
* **Cloud Database:** MySQL ( clever cloud [https://www.clever.cloud/product/mysql/](https://www.clever.cloud/product/mysql/) )  
  * Used to store persistent data such as properties, payment records.   
* **Version Control:** Git
  * Used to track incremental development progress and changes throughout the project
