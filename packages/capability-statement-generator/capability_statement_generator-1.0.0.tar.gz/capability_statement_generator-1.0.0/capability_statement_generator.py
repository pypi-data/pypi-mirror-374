#!/usr/bin/env python3
"""
Capability Statement Form Generator
Automated form creation and data population for company capability statements
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class CompanyInfo:
    """Company basic information"""
    company_name: str
    company_number: str
    phone: str
    email: str
    website: str
    address_line1: str
    address_line2: str
    
@dataclass
class ServiceOffering:
    """Individual service offering"""
    name: str
    description: str

@dataclass
class Client:
    """Featured client information"""
    name: str
    description: str

@dataclass
class Certification:
    """Company certification"""
    name: str
    description: str

@dataclass
class PastPerformance:
    """Past performance example"""
    title: str
    description: str

@dataclass
class CapabilityStatement:
    """Complete capability statement data structure"""
    company_info: CompanyInfo
    executive_summary: str
    services: List[ServiceOffering]
    differentiators: List[str]
    strengths_commitments: List[str]
    featured_clients: List[Client]
    certifications: List[Certification]
    past_performances: List[PastPerformance]
    created_date: str

class CapabilityStatementForm:
    """Form generator and data handler for capability statements"""
    
    def __init__(self):
        self.data = None
        
    def create_pharmatech_statement(self) -> CapabilityStatement:
        """Create capability statement with PharmaTech Innovations data"""
        
        # Company Information
        company_info = CompanyInfo(
            company_name="PharmaTech Innovations Ltd.",
            company_number="98765432",
            phone="+1(00) 000 000 0000",
            email="myownemail@pharmatech.com",
            website="pharmatechinnovations.com",
            address_line1="123 Street Name, City",
            address_line2="21345 California"
        )
        
        # Executive Summary
        executive_summary = """PharmaTech Innovations Ltd. excels in developing cutting-edge pharmaceutical solutions that significantly improve health outcomes. Our experienced team drives innovation, ensuring products meet stringent industry standards and comply with regulatory requirements.

Positioned as market leaders, our robust stock performance and global presence underscore our commitment to excellence and growth. We provide tailored solutions, leveraging our expertise to deliver superior quality and customer satisfaction."""
        
        # Services
        services = [
            ServiceOffering(
                "Regulatory Compliance",
                "Ensure your products meet all relevant regulations effortlessly."
            ),
            ServiceOffering(
                "Technical Documentation", 
                "Professional documentation tailored for clarity and precision."
            ),
            ServiceOffering(
                "Research & Development",
                "Innovative solutions to advance your pharmaceutical research."
            ),
            ServiceOffering(
                "Quality Assurance",
                "Uncompromising quality checks to maintain industry standards."
            )
        ]
        
        # Differentiators
        differentiators = [
            "Cutting-Edge R&D: Utilizing advanced AI and machine learning technologies to significantly speed up the processes of drug discovery and development, allowing for quicker time-to-market for innovative treatments.",
            "Collaborative Network: Partnering with global pharmaceutical companies, leading biotech firms, and renowned research institutions to foster a synergistic environment that drives toward groundbreaking advancements.",
            "Regulatory Expertise: Successfully navigating complex regulatory landscapes with a consistent and proven compliance record, ensuring that all products meet stringent international standards and receive timely approvals.",
            "Personalized Solutions: Providing customized, patient-centric healthcare approaches that significantly improve individual health outcomes by tailoring treatments to the unique genetic and environmental factors."
        ]
        
        # Strengths and Commitments
        strengths_commitments = [
            "Innovative Technologies: Emphasize the use of pioneering technologies like CRISPR, nanotechnology, and bioprinting to revolutionize drug development.",
            "Global Reach: Showcase the company's international presence and ability to operate seamlessly across different markets.",
            "Sustainability Commitment: Detail efforts towards sustainable practices in production and distribution, highlighting environmental responsibility.",
            "Customer Focus: Underscore a commitment to exceptional client service and long-term partnerships, ensuring that client needs are consistently met."
        ]
        
        # Featured Clients
        featured_clients = [
            Client(
                "Global Pharmaceutical Leader",
                "Partnering with one of the top five pharmaceutical companies worldwide to develop groundbreaking oncology treatments."
            ),
            Client(
                "Biotech Innovators",
                "Collaborating with a cutting-edge biotechnology firm to advance gene therapy solutions. Improvements are already noted and documented."
            ),
            Client(
                "Healthcare Systems",
                "Supporting a leading healthcare network in implementing AI-driven diagnostic tools to enhance patient care. Benefits for the clients are huge."
            ),
            Client(
                "Research Institutions",
                "Working with renowned research universities to accelerate drug discovery and development through advanced data analytics."
            )
        ]
        
        # Certifications
        certifications = [
            Certification(
                "ISO 13485:2016",
                "Medical devices - Quality management systems - Requirements for regulatory purposes."
            ),
            Certification(
                "Good Manufacturing Practice (GMP)",
                "Ensuring products are consistently produced and controlled according to quality standards."
            ),
            Certification(
                "FDA Approval",
                "Compliance with the U.S. Food and Drug Administration for pharmaceuticals and medical devices."
            ),
            Certification(
                "CE Marking",
                "Conformity with health, safety, and environmental protection standards for products sold within the European Economic Area."
            ),
            Certification(
                "ISO 9001:2015",
                "Globally recognized standard for quality management systems, ensuring consistent improvement and adherence to regulatory requirements."
            ),
            Certification(
                "ICH Q7 Compliance",
                "International Council for Harmonisation guidelines for active pharmaceutical ingredients."
            )
        ]
        
        # Past Performances
        past_performances = [
            PastPerformance(
                "Gene Therapy Advancements",
                "Worked with a pioneering biotechnology firm to bring a revolutionary gene therapy product to market, which provided a new treatment option for patients with rare genetic disorders."
            ),
            PastPerformance(
                "AI-Driven Diagnostic Tools",
                "Implemented AI-driven diagnostic tools in a leading healthcare network, enhancing early detection and improving patient outcomes across multiple medical facilities."
            )
        ]
        
        # Create complete capability statement
        capability_statement = CapabilityStatement(
            company_info=company_info,
            executive_summary=executive_summary,
            services=services,
            differentiators=differentiators,
            strengths_commitments=strengths_commitments,
            featured_clients=featured_clients,
            certifications=certifications,
            past_performances=past_performances,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.data = capability_statement
        return capability_statement
    
    def display_form_data(self, statement: CapabilityStatement) -> None:
        """Display the capability statement in a formatted way"""
        
        print("=" * 80)
        print("CAPABILITY STATEMENT FORM")
        print("=" * 80)
        
        # Company Information
        print("\n📋 COMPANY INFORMATION")
        print("-" * 40)
        print(f"Company Name: {statement.company_info.company_name}")
        print(f"Company Number: {statement.company_info.company_number}")
        print(f"Phone: {statement.company_info.phone}")
        print(f"Email: {statement.company_info.email}")
        print(f"Website: {statement.company_info.website}")
        print(f"Address: {statement.company_info.address_line1}")
        print(f"         {statement.company_info.address_line2}")
        
        # Executive Summary
        print("\n📊 EXECUTIVE SUMMARY")
        print("-" * 40)
        print(statement.executive_summary)
        
        # Services
        print("\n🔧 SERVICES OFFERED")
        print("-" * 40)
        for i, service in enumerate(statement.services, 1):
            print(f"{i}. {service.name}")
            print(f"   {service.description}")
            print()
        
        # Differentiators
        print("🌟 KEY DIFFERENTIATORS")
        print("-" * 40)
        for i, diff in enumerate(statement.differentiators, 1):
            print(f"{i}. {diff}")
            print()
        
        # Strengths and Commitments
        print("💪 STRENGTHS AND COMMITMENTS")
        print("-" * 40)
        for i, strength in enumerate(statement.strengths_commitments, 1):
            print(f"{i}. {strength}")
            print()
        
        # Featured Clients
        print("👥 FEATURED CLIENTS")
        print("-" * 40)
        for i, client in enumerate(statement.featured_clients, 1):
            print(f"{i}. {client.name}")
            print(f"   {client.description}")
            print()
        
        # Certifications
        print("🏆 CERTIFICATIONS")
        print("-" * 40)
        for i, cert in enumerate(statement.certifications, 1):
            print(f"{i}. {cert.name}")
            print(f"   {cert.description}")
            print()
        
        # Past Performances
        print("📈 PAST PERFORMANCES")
        print("-" * 40)
        for i, perf in enumerate(statement.past_performances, 1):
            print(f"{i}. {perf.title}")
            print(f"   {perf.description}")
            print()
        
        print(f"\nForm Created: {statement.created_date}")
        print("=" * 80)
    
    def export_to_json(self, filename: str = "capability_statement.json") -> None:
        """Export capability statement to JSON file"""
        if self.data:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.data), f, indent=2, ensure_ascii=False)
            print(f"\n✅ Capability statement exported to {filename}")
        else:
            print("❌ No data to export. Please create a capability statement first.")
    
    def get_form_template(self) -> Dict[str, Any]:
        """Return a blank form template for manual filling"""
        template = {
            "company_info": {
                "company_name": "",
                "company_number": "",
                "phone": "",
                "email": "",
                "website": "",
                "address_line1": "",
                "address_line2": ""
            },
            "executive_summary": "",
            "services": [
                {"name": "", "description": ""}
            ],
            "differentiators": [""],
            "strengths_commitments": [""],
            "featured_clients": [
                {"name": "", "description": ""}
            ],
            "certifications": [
                {"name": "", "description": ""}
            ],
            "past_performances": [
                {"title": "", "description": ""}
            ]
        }
        return template

def main():
    """Main function to demonstrate the capability statement form"""
    
    # Create form generator
    form_generator = CapabilityStatementForm()
    
    # Create PharmaTech capability statement
    print("Creating PharmaTech Innovations Capability Statement...")
    pharmatech_statement = form_generator.create_pharmatech_statement()
    
    # Display the filled form
    form_generator.display_form_data(pharmatech_statement)
    
    # Export to JSON
    form_generator.export_to_json("pharmatech_capability_statement.json")
    
    # Show template structure
    print("\n" + "=" * 80)
    print("BLANK FORM TEMPLATE STRUCTURE")
    print("=" * 80)
    template = form_generator.get_form_template()
    print(json.dumps(template, indent=2))
    
    return pharmatech_statement

if __name__ == "__main__":
    capability_statement = main()
    print("\n🎉 Capability Statement Form completed successfully!")
    print("📄 Data structure created and populated with PharmaTech information.")
    print("💾 JSON export file generated for easy data transfer.")
