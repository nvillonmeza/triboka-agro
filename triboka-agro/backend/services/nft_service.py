"""
NFT Service for Triboka BaaS Platform
Business logic for NFT certificate management
"""

import json
from datetime import datetime, timedelta
from sqlalchemy import func

from models.models import NFTCertificate, Company, Lot, db
from config.config import Config

class NFTService:
    def __init__(self):
        self.config = Config.get_instance()
    
    def can_mint_nft(self, company):
        """Check if company can mint NFT based on plan limits"""
        # Get monthly NFT count
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_nfts = NFTCertificate.query.filter(
            NFTCertificate.company_id == company.id,
            NFTCertificate.is_minted == True,
            NFTCertificate.mint_date >= current_month
        ).count()
        
        # Get plan limits
        plan_limits = {
            'starter': 50,
            'professional': 200,
            'enterprise': -1  # Unlimited
        }
        
        limit = plan_limits.get(company.subscription_plan, 0)
        
        # Unlimited plan
        if limit == -1:
            return True
        
        return monthly_nfts < limit
    
    def get_monthly_nft_usage(self, company_id):
        """Get monthly NFT usage statistics"""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_nfts = NFTCertificate.query.filter(
            NFTCertificate.company_id == company_id,
            NFTCertificate.is_minted == True,
            NFTCertificate.mint_date >= current_month
        ).count()
        
        return {
            'current_month': current_month.strftime('%Y-%m'),
            'nfts_minted': monthly_nfts,
            'period': 'monthly'
        }
    
    def charge_nft_commission(self, company, nft_certificate):
        """Charge commission for NFT minting"""
        commission_amount = self.config.NFT_COMMISSION_USD
        
        # In a real implementation, this would integrate with payment processor
        # For now, we'll just log the charge
        print(f"Charging ${commission_amount} commission to {company.name} for NFT {nft_certificate.token_id}")
        
        # Update company billing
        if not hasattr(company, 'total_nft_charges'):
            company.total_nft_charges = 0
        
        company.total_nft_charges += commission_amount
        db.session.commit()
        
        return {
            'charged': True,
            'amount': commission_amount,
            'currency': 'USD',
            'description': f'NFT Certificate: {nft_certificate.title}'
        }
    
    def generate_metadata(self, nft_certificate):
        """Generate NFT metadata structure"""
        metadata = {
            'name': nft_certificate.title,
            'description': nft_certificate.description or f'{nft_certificate.certificate_type.title()} Certificate for Lot {nft_certificate.lot.lot_number}',
            'image': nft_certificate.image_url or self._get_default_image_url(nft_certificate.certificate_type),
            'external_url': f"{self.config.API_BASE_URL}/nfts/{nft_certificate.uuid}/verify",
            'attributes': self._generate_attributes(nft_certificate),
            'properties': {
                'certificate_type': nft_certificate.certificate_type,
                'token_id': nft_certificate.token_id,
                'issuer': nft_certificate.company.name,
                'issue_date': nft_certificate.created_at.isoformat(),
                'verification_url': f"{self.config.API_BASE_URL}/nfts/{nft_certificate.uuid}/verify"
            }
        }
        
        # Store metadata URI
        metadata_uri = f"{self.config.API_BASE_URL}/nfts/{nft_certificate.uuid}/metadata"
        
        return {
            'metadata': metadata,
            'uri': metadata_uri
        }
    
    def get_nft_metadata(self, nft_certificate):
        """Get formatted NFT metadata for OpenSea compatibility"""
        return {
            'name': nft_certificate.title,
            'description': nft_certificate.description or f'{nft_certificate.certificate_type.title()} Certificate for Lot {nft_certificate.lot.lot_number}',
            'image': nft_certificate.image_url or self._get_default_image_url(nft_certificate.certificate_type),
            'external_url': f"{self.config.API_BASE_URL}/nfts/{nft_certificate.uuid}/verify",
            'attributes': self._generate_attributes(nft_certificate),
            'background_color': self._get_certificate_color(nft_certificate.certificate_type),
            'animation_url': None,  # Could add certificate animation
            'youtube_url': None
        }
    
    def _generate_attributes(self, nft_certificate):
        """Generate NFT attributes array"""
        attributes = [
            {
                'trait_type': 'Certificate Type',
                'value': nft_certificate.certificate_type.title()
            },
            {
                'trait_type': 'Lot Number',
                'value': nft_certificate.lot.lot_number
            },
            {
                'trait_type': 'Origin',
                'value': nft_certificate.lot.origin_location
            },
            {
                'trait_type': 'Quantity',
                'value': nft_certificate.lot.quantity_kg,
                'display_type': 'number',
                'max_value': 10000
            },
            {
                'trait_type': 'Issuer',
                'value': nft_certificate.company.name
            },
            {
                'trait_type': 'Issue Year',
                'value': nft_certificate.created_at.year,
                'display_type': 'date'
            },
            {
                'trait_type': 'Status',
                'value': 'Minted' if nft_certificate.is_minted else 'Pending'
            }
        ]
        
        # Add quality grade if available
        if nft_certificate.lot.quality_grade:
            attributes.append({
                'trait_type': 'Quality Grade',
                'value': nft_certificate.lot.quality_grade
            })
        
        # Add harvest information
        if nft_certificate.lot.harvest_date:
            attributes.append({
                'trait_type': 'Harvest Season',
                'value': self._get_harvest_season(nft_certificate.lot.harvest_date)
            })
            
            attributes.append({
                'trait_type': 'Harvest Year',
                'value': nft_certificate.lot.harvest_date.year,
                'display_type': 'date'
            })
        
        # Add processing information
        if nft_certificate.lot.processing_method:
            attributes.append({
                'trait_type': 'Processing Method',
                'value': nft_certificate.lot.processing_method
            })
        
        # Add certification rarity
        attributes.append({
            'trait_type': 'Rarity',
            'value': self._calculate_rarity(nft_certificate)
        })
        
        return attributes
    
    def _get_default_image_url(self, certificate_type):
        """Get default image URL for certificate type"""
        base_url = f"{self.config.API_BASE_URL}/static/certificates"
        
        image_map = {
            'origin': f"{base_url}/origin-certificate.png",
            'quality': f"{base_url}/quality-certificate.png",
            'organic': f"{base_url}/organic-certificate.png",
            'fairtrade': f"{base_url}/fairtrade-certificate.png",
            'export': f"{base_url}/export-certificate.png",
            'delivery': f"{base_url}/delivery-certificate.png"
        }
        
        return image_map.get(certificate_type, f"{base_url}/default-certificate.png")
    
    def _get_certificate_color(self, certificate_type):
        """Get background color for certificate type"""
        color_map = {
            'origin': '8B4513',      # Brown
            'quality': '228B22',     # Forest Green
            'organic': '32CD32',     # Lime Green
            'fairtrade': 'FF6347',   # Tomato
            'export': '4169E1',      # Royal Blue
            'delivery': '9370DB'     # Medium Purple
        }
        
        return color_map.get(certificate_type, '696969')  # Dim Gray
    
    def _get_harvest_season(self, harvest_date):
        """Determine harvest season from date"""
        month = harvest_date.month
        
        if month in [12, 1, 2]:
            return 'Dry Season'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Wet Season'
        else:
            return 'Late Season'
    
    def _calculate_rarity(self, nft_certificate):
        """Calculate certificate rarity based on various factors"""
        rarity_score = 0
        
        # Quality grade rarity
        quality_scores = {
            'AAA': 5,
            'AA': 4,
            'A': 3,
            'B': 2,
            'C': 1
        }
        rarity_score += quality_scores.get(nft_certificate.lot.quality_grade, 0)
        
        # Origin rarity (some regions are rarer)
        rare_origins = ['Chuao', 'Nacional', 'Criollo', 'Porcelana']
        if any(origin in nft_certificate.lot.origin_location for origin in rare_origins):
            rarity_score += 3
        
        # Quantity rarity (smaller lots are rarer)
        if nft_certificate.lot.quantity_kg < 100:
            rarity_score += 3
        elif nft_certificate.lot.quantity_kg < 500:
            rarity_score += 2
        elif nft_certificate.lot.quantity_kg < 1000:
            rarity_score += 1
        
        # Age rarity (older lots become rarer)
        age_months = (datetime.utcnow() - nft_certificate.created_at).days / 30
        if age_months > 12:
            rarity_score += 2
        elif age_months > 6:
            rarity_score += 1
        
        # Determine rarity level
        if rarity_score >= 10:
            return 'Legendary'
        elif rarity_score >= 7:
            return 'Epic'
        elif rarity_score >= 5:
            return 'Rare'
        elif rarity_score >= 3:
            return 'Uncommon'
        else:
            return 'Common'
    
    def get_company_nft_stats(self, company_id):
        """Get comprehensive NFT statistics for a company"""
        # Basic counts
        total_nfts = NFTCertificate.query.filter_by(company_id=company_id).count()
        minted_nfts = NFTCertificate.query.filter_by(company_id=company_id, is_minted=True).count()
        pending_nfts = total_nfts - minted_nfts
        
        # Monthly statistics
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_minted = NFTCertificate.query.filter(
            NFTCertificate.company_id == company_id,
            NFTCertificate.is_minted == True,
            NFTCertificate.mint_date >= current_month
        ).count()
        
        # Certificate type distribution
        type_stats = db.session.query(
            NFTCertificate.certificate_type,
            func.count(NFTCertificate.id).label('count')
        ).filter_by(company_id=company_id).group_by(NFTCertificate.certificate_type).all()
        
        type_distribution = {stat.certificate_type: stat.count for stat in type_stats}
        
        # Recent activity
        recent_nfts = NFTCertificate.query.filter_by(company_id=company_id).order_by(
            NFTCertificate.created_at.desc()
        ).limit(5).all()
        
        recent_activity = [
            {
                'uuid': nft.uuid,
                'title': nft.title,
                'certificate_type': nft.certificate_type,
                'is_minted': nft.is_minted,
                'created_at': nft.created_at.isoformat(),
                'lot_number': nft.lot.lot_number
            }
            for nft in recent_nfts
        ]
        
        # Revenue calculation (commissions)
        total_commission = minted_nfts * self.config.NFT_COMMISSION_USD
        monthly_commission = monthly_minted * self.config.NFT_COMMISSION_USD
        
        return {
            'total_certificates': total_nfts,
            'minted_certificates': minted_nfts,
            'pending_certificates': pending_nfts,
            'monthly_minted': monthly_minted,
            'minting_rate': round((minted_nfts / total_nfts * 100) if total_nfts > 0 else 0, 2),
            'type_distribution': type_distribution,
            'recent_activity': recent_activity,
            'revenue': {
                'total_commission_usd': total_commission,
                'monthly_commission_usd': monthly_commission,
                'commission_per_nft': self.config.NFT_COMMISSION_USD
            }
        }
    
    def validate_certificate_data(self, certificate_type, lot_data):
        """Validate if lot data supports certificate type"""
        validations = {
            'origin': lambda lot: bool(lot.origin_location),
            'quality': lambda lot: bool(lot.quality_grade),
            'organic': lambda lot: bool(lot.certifications and 'organic' in lot.certifications.lower()),
            'fairtrade': lambda lot: bool(lot.certifications and 'fairtrade' in lot.certifications.lower()),
            'export': lambda lot: bool(lot.export_date),
            'delivery': lambda lot: bool(lot.delivery_date)
        }
        
        validator = validations.get(certificate_type)
        if not validator:
            return False, f"Unknown certificate type: {certificate_type}"
        
        if not validator(lot_data):
            return False, f"Lot data insufficient for {certificate_type} certificate"
        
        return True, "Valid"