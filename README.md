Enterprise Endpoint Security Operations Platform (EESOP)

EESOP — Enterprise Endpoint Security Operations Platform

Developed by Darshayu Global Solutions

EESOP is a security operations platform prototype designed to centralize endpoint security visibility, incident management, policy management, remediation workflows, response actions, and security auditing within a single operational interface.

Overview

Modern enterprise endpoint environments generate large volumes of security telemetry, incidents, policy events, compliance data, and remediation requirements.

EESOP provides a centralized security operations workflow for managing these activities across enterprise endpoints.

The platform combines:

Endpoint security visibility

Endpoint risk monitoring

Security incident management

Response action workflows

Security policy management

Remediation workflows

Role-Based Access Control (RBAC)

Security activity auditing

Endpoint security compliance monitoring

EESOP is designed as a portfolio and learning project demonstrating practical Endpoint Security, Security Operations, Incident Response, Security Engineering, Detection Engineering, and automation concepts.

Vision

To provide a centralized enterprise platform for:

Endpoint Protection

Incident Response

Threat Management

Security Engineering

Detection Engineering

Security Operations

Compliance Monitoring

Security Automation

Operational Excellence

Key Capabilities

1. Security Operations Dashboard

The EESOP dashboard provides a centralized security overview including:

Total Endpoints

Microsoft Defender Coverage

CrowdStrike Coverage

BitLocker Compliance

High-Risk Endpoints

Open Security Incidents

SLA Compliance

Average Risk Score

Critical Incident Queue

Compliance Dashboard

Recent Security Activities

The dashboard provides security teams with a consolidated operational view of the endpoint environment.

2. Endpoint 360

Endpoint 360 provides a consolidated view of an individual endpoint.

The platform is designed to bring endpoint-related security information together, including:

Endpoint identity

Security status

Security tools

Risk information

Incidents

Threat information

Timeline activity

Engineering information

Security actions

Policy information

Remediation activity

This provides a security analyst with a centralized endpoint investigation view.

3. Incident Management

EESOP provides an incident-management workflow for security operations teams.

Capabilities include:

Incident identification

Incident severity

Incident status

Detection source

Endpoint association

Incident investigation

Response action requests

Incident response tracking

SLA tracking

Security timeline auditing

The platform supports a controlled workflow where security personnel can request response actions while execution privileges remain restricted according to RBAC.

4. Response Actions

Response actions provide a controlled mechanism for responding to security incidents.

Example response activities can include:

Endpoint isolation

Process termination

Threat remediation

Security investigation actions

The workflow separates:

Request
   ↓
Authorization
   ↓
Execution
   ↓
Result
   ↓
Audit

This demonstrates separation of duties within a security operations environment.

5. Policy Management

EESOP provides endpoint security policy management capabilities.

Security teams can work with:

Policy configuration

Current values

Desired values

Policy status

Deployment status

Risk level

Change reason

Policy audit information

The policy workflow follows:

Policy Review
      ↓
Policy Tuning
      ↓
Deployment
      ↓
Validation
      ↓
Audit

Policy changes are controlled through role-based permissions.

6. Remediation Center

The Remediation Center provides a controlled workflow for security remediation scripts.

Capabilities include:

Script library

Script categorization

Tool association

Risk classification

Deployment requests

Approval workflow

Execution tracking

Validation

Deployment history

Audit information

The workflow follows:

Request
   ↓
Security Lead Approval
   ↓
Execution
   ↓
Validation
   ↓
Audit Timeline

The current V1 implementation simulates script deployment and execution rather than executing scripts against production endpoints.

Role-Based Access Control

EESOP implements role-based access control to separate security responsibilities.

Security Analyst

Analysts can:

View endpoints

View security policies

Investigate incidents

Request response actions

Request remediation

View security timelines

Analysts cannot directly:

Deploy policies

Validate policies

Execute response actions

Approve remediation deployments

Execute remediation deployments

Validate remediation deployments

Security Engineer

Security Engineers can:

Investigate incidents

Tune policies

Deploy policies

Validate policies

Execute remediation workflows

Validate remediation

Perform engineering-related security operations

Security Lead

Security Leads can:

Perform engineering security operations

Approve remediation deployments

Manage response workflows

Validate security changes

Oversee remediation activities

Administrator

The Administrator role provides platform-level access to the available operational functionality.

Security Workflows

EESOP follows controlled operational workflows rather than allowing every user to directly modify security controls.

Incident Response

Security Detection
       ↓
Incident
       ↓
Investigation
       ↓
Response Request
       ↓
Authorized Execution
       ↓
Result
       ↓
Audit Timeline

Policy Management

Policy
  ↓
Review
  ↓
Tune
  ↓
Deploy
  ↓
Validate
  ↓
Audit

Remediation

Remediation Request
        ↓
Lead Approval
        ↓
Execution
        ↓
Validation
        ↓
Audit

RBAC and Separation of Duties

One of the core security concepts demonstrated by EESOP is separation of duties.

For example:

Security Analyst
      │
      └── Request remediation
              ↓
        Security Lead
              │
              └── Approve
                    ↓
             Security Engineer
                    │
                    └── Execute
                          ↓
                      Validation
                          ↓
                     Audit

This prevents a single operational role from automatically performing every stage of a privileged security workflow.

Audit and Security Timeline

Security-related operations are recorded through the EESOP audit/timeline mechanisms.

The timeline can capture information such as:

Endpoint

Event time

Event type

Event category

Event source

Severity

Description

User who performed the action

This provides traceability for security operations and administrative activity.

Technology Stack

Application

Python

Streamlit

Data

SQLite

Pandas

Security Operations Concepts

Endpoint Security

EDR/XDR

Incident Response

Security Policy Management

Remediation

RBAC

Security Auditing

SLA Monitoring

Risk Scoring

Endpoint Security Technologies Represented

Microsoft Defender

CrowdStrike

BitLocker

Endpoint Security Policies

Endpoint Remediation

Project Architecture

The project follows a layered structure separating the user interface, business logic, repositories, and database.

EESOP/
│
├── app.py
│
├── pages/
│   ├── 1_Endpoint_360.py
│   ├── 2_Policy_Management.py
│   ├── 3_Remediation_Center.py
│   └── 4_Incident_Management.py
│
├── endpoint_operations/
│   ├── Endpoint Services
│   ├── Incident Services
│   ├── Policy Services
│   ├── Remediation Services
│   ├── Response Action Services
│   ├── Timeline Services
│   └── Security Services
│
├── services/
│   ├── Authentication
│   ├── Authorization
│   ├── Dashboard Services
│   └── Security Services
│
├── database/
│   └── Database Connection / Repository Layer
│
├── data/
├── telemetry/
├── scripts/
├── playbooks/
├── tests/
└── docs/

The application separates UI functionality from service and repository layers to make the platform easier to extend.

Database

EESOP uses SQLite for the V1 prototype.

The database contains operational entities covering areas such as:

Regions

Countries

Offices

Departments

Users

Devices

Endpoint Security Status

Endpoint Timeline

Incidents

Threats

Engineering Activities

Endpoint Actions

Endpoint Policies

Remediation Scripts

Script Deployments

Role Permissions

Platform Users

Incident Response Actions

Authentication Sessions

Authentication

EESOP provides application authentication with persistent browser session handling.

The application supports:

Login

Logout

Session restoration

Protected pages

Role identification

Permission checks

Protected application pages are not exposed to unauthenticated users.

Installation

1. Clone the repository

git clone <repository-url>
cd EESOP

2. Create a virtual environment

Windows

python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

Linux/macOS

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

Running EESOP

Start the Streamlit application:

streamlit run app.py

The application will start locally and provide the EESOP login interface.

Demo Roles

The V1 prototype contains separate users representing different security responsibilities:

Username

Role

analyst

Security Analyst

engineer

Security Engineer

lead

Security Lead

admin

EESOP Administrator

Security note: Demo credentials should be managed according to the application's authentication configuration and should never be committed to source control.

Current V1 Scope

The current version focuses on demonstrating the architecture and operational workflows of an enterprise endpoint security platform.

Included:

Authentication

Persistent sessions

RBAC

Endpoint visibility

Security dashboard

Incident management

Response action workflow

Policy management

Remediation workflow

Approval workflow

Validation workflow

Security timeline

Risk monitoring

Compliance monitoring

SQLite persistence

Important V1 Limitation

EESOP V1 is a security operations prototype.

Endpoint telemetry, policy deployment, remediation execution, and response execution are represented through application workflows and simulated operational actions.

The application does not currently execute security remediation commands against a production enterprise endpoint environment.

The architecture is designed so that future versions can integrate with real endpoint security APIs and enterprise management platforms.

Future Enhancements

Potential future versions can integrate:

Microsoft Defender for Endpoint API

CrowdStrike Falcon API

Microsoft Intune

Tanium

ServiceNow

Microsoft Sentinel

Splunk

Real endpoint telemetry

Automated threat ingestion

Automated incident creation

Real remediation execution

Endpoint isolation

Automated playbooks

Advanced detection engineering

MITRE ATT&CK mapping

NIST security framework mapping

SIEM integration

Automated SLA monitoring

Security analytics

Production-grade authentication

Enterprise database backend

Security Design Principles

EESOP demonstrates several practical security engineering principles:

Least privilege

Role-based access control

Separation of duties

Controlled privileged operations

Auditability

Security monitoring

Risk-based prioritization

Incident response workflow

Change management

Remediation validation

Project Status

Version: 1.0

Status: Functional V1 Prototype

The current version demonstrates the core security operations workflows and RBAC model required for an enterprise endpoint security operations platform.

Author

Darshit Goyal

Developed under:

Darshayu Global Solutions

Disclaimer

EESOP is an educational and portfolio security engineering project.

It is not intended to replace enterprise-grade endpoint security, EDR, SIEM, IAM, ITSM, or security orchestration platforms.