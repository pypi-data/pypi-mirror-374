"""
Helper utilities for LangChain Hedera integration
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


def format_analysis_output(
    data: Dict[str, Any],
    output_format: str = "markdown",
    include_metadata: bool = True
) -> str:
    """Format analysis output for different presentation formats.
    
    Args:
        data: Analysis data to format
        output_format: Output format ('markdown', 'json', 'text')
        include_metadata: Whether to include metadata in output
    
    Returns:
        Formatted string output
    """
    if output_format == "json":
        return json.dumps(data, indent=2, default=str)
    
    elif output_format == "markdown":
        return _format_as_markdown(data, include_metadata)
    
    elif output_format == "text":
        return _format_as_text(data, include_metadata)
    
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def _format_as_markdown(data: Dict[str, Any], include_metadata: bool) -> str:
    """Format data as markdown."""
    md_lines = []
    
    if include_metadata:
        md_lines.append(f"# Hedera DeFi Analysis Report")
        md_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Handle different analysis types
    if "ecosystem_health" in data:
        md_lines.append(f"## Ecosystem Health: {data['ecosystem_health'].title()}")
        md_lines.append(f"**Total TVL:** ${data.get('total_tvl_usd', 0):,.2f}\n")
    
    if "top_protocols" in data:
        md_lines.append("## Top Protocols")
        for i, protocol in enumerate(data["top_protocols"][:5], 1):
            md_lines.append(f"{i}. **{protocol.get('name', 'Unknown')}** ({protocol.get('type', 'Unknown')})")
            md_lines.append(f"   - TVL: ${protocol.get('tvl_usd', 0):,.2f}")
            md_lines.append(f"   - Performance: {protocol.get('performance_rating', 'N/A')}")
    
    if "top_opportunities" in data:
        md_lines.append("\n## Investment Opportunities")
        for i, opp in enumerate(data["top_opportunities"][:5], 1):
            md_lines.append(f"{i}. **{opp.get('asset', 'Unknown')}** on {opp.get('protocol', 'Unknown')}")
            md_lines.append(f"   - Type: {opp.get('type', 'Unknown')}")
            md_lines.append(f"   - Expected APY: {opp.get('expected_apy', 0):.2f}%")
            md_lines.append(f"   - Risk Level: {opp.get('risk_level', 'Unknown')}")
    
    if "risk_factors" in data:
        md_lines.append("\n## Risk Factors")
        for risk in data["risk_factors"]:
            md_lines.append(f"- {risk}")
    
    if "recommendations" in data:
        md_lines.append("\n## Recommendations")
        for rec in data["recommendations"]:
            md_lines.append(f"- {rec}")
    
    return "\n".join(md_lines)


def _format_as_text(data: Dict[str, Any], include_metadata: bool) -> str:
    """Format data as plain text."""
    lines = []
    
    if include_metadata:
        lines.append("HEDERA DEFI ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
    
    # Format key metrics
    if "total_tvl_usd" in data:
        lines.append(f"Total TVL: ${data['total_tvl_usd']:,.2f}")
    
    if "ecosystem_health" in data:
        lines.append(f"Ecosystem Health: {data['ecosystem_health'].upper()}")
    
    # Add other sections as plain text
    for key, value in data.items():
        if key not in ["total_tvl_usd", "ecosystem_health"] and isinstance(value, (list, dict)):
            lines.append(f"\n{key.replace('_', ' ').title()}:")
            if isinstance(value, list):
                for item in value[:5]:  # Limit to top 5
                    if isinstance(item, dict):
                        lines.append(f"  - {item.get('name', item.get('symbol', str(item)))}")
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                for k, v in list(value.items())[:5]:  # Limit to top 5
                    lines.append(f"  {k}: {v}")
    
    return "\n".join(lines)


def calculate_risk_score(
    protocol_data: Dict[str, Any],
    market_data: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate risk score for a protocol or opportunity.
    
    Args:
        protocol_data: Protocol-specific risk factors
        market_data: Market-wide risk factors
        weights: Custom weights for risk factors
    
    Returns:
        Risk score from 0-100 (higher = more risky)
    """
    default_weights = {
        "tvl_concentration": 0.2,
        "protocol_age": 0.15,
        "audit_status": 0.25,
        "liquidity_depth": 0.15,
        "market_volatility": 0.15,
        "governance_risk": 0.1,
    }
    
    weights = weights or default_weights
    risk_score = 0.0
    
    # TVL concentration risk (0-30 points)
    tvl = protocol_data.get("tvl_usd", 0)
    market_tvl = market_data.get("total_tvl_usd", 1)
    concentration = (tvl / market_tvl) * 100 if market_tvl > 0 else 0
    
    if concentration > 50:  # Highly concentrated
        tvl_risk = 30
    elif concentration > 25:
        tvl_risk = 20
    elif concentration > 10:
        tvl_risk = 10
    else:
        tvl_risk = 5
    
    risk_score += tvl_risk * weights.get("tvl_concentration", 0.2)
    
    # Protocol age risk (0-25 points)
    created_at = protocol_data.get("created_at")
    if created_at:
        try:
            if isinstance(created_at, str):
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_date = created_at
            
            age_days = (datetime.now() - created_date.replace(tzinfo=None)).days
            
            if age_days < 30:  # Very new
                age_risk = 25
            elif age_days < 90:  # New
                age_risk = 15
            elif age_days < 365:  # Established
                age_risk = 5
            else:  # Mature
                age_risk = 0
        except:
            age_risk = 20  # Unknown age = moderate risk
    else:
        age_risk = 20
    
    risk_score += age_risk * weights.get("protocol_age", 0.15)
    
    # Liquidity depth risk (0-20 points)
    volume_24h = protocol_data.get("volume_24h", 0)
    if tvl > 0:
        volume_ratio = volume_24h / tvl
        if volume_ratio < 0.01:  # Very low volume
            liquidity_risk = 20
        elif volume_ratio < 0.05:
            liquidity_risk = 10
        elif volume_ratio < 0.1:
            liquidity_risk = 5
        else:
            liquidity_risk = 0
    else:
        liquidity_risk = 20
    
    risk_score += liquidity_risk * weights.get("liquidity_depth", 0.15)
    
    # Market volatility risk (0-15 points)
    market_health = market_data.get("ecosystem_health", "unknown")
    volatility_risk = {
        "excellent": 0,
        "good": 3,
        "moderate": 8,
        "poor": 15,
        "unknown": 10
    }.get(market_health, 10)
    
    risk_score += volatility_risk * weights.get("market_volatility", 0.15)
    
    # Protocol type risk (0-10 points)
    protocol_type = protocol_data.get("type", "unknown")
    type_risk = {
        "staking": 2,     # Lowest risk
        "dex": 5,         # Medium risk
        "lending": 8,     # Higher risk
        "unknown": 10     # Highest risk
    }.get(protocol_type, 10)
    
    risk_score += type_risk * weights.get("governance_risk", 0.1)
    
    return min(100, max(0, risk_score))  # Clamp to 0-100


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amounts consistently."""
    if currency.upper() == "USD":
        return f"${amount:,.2f}"
    elif currency.upper() == "HBAR":
        return f"{amount:,.4f} HBAR"
    else:
        return f"{amount:,.4f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage values consistently."""
    return f"{value:.{decimals}f}%"


def format_risk_level(risk_score: float) -> str:
    """Convert numeric risk score to qualitative level."""
    if risk_score <= 20:
        return "Low"
    elif risk_score <= 40:
        return "Medium-Low"
    elif risk_score <= 60:
        return "Medium"
    elif risk_score <= 80:
        return "Medium-High"
    else:
        return "High"


def calculate_apy_adjusted_for_risk(apy: float, risk_score: float) -> float:
    """Calculate risk-adjusted APY."""
    risk_multiplier = max(0.1, (100 - risk_score) / 100)
    return apy * risk_multiplier


def validate_hedera_account_id(account_id: str) -> bool:
    """Validate Hedera account ID format."""
    import re
    pattern = r"^0\.0\.\d+$"
    return bool(re.match(pattern, account_id))


def parse_token_amount(amount_str: str, decimals: int = 8) -> float:
    """Parse token amount string to float considering decimals."""
    try:
        amount_int = int(amount_str)
        return amount_int / (10 ** decimals)
    except (ValueError, TypeError):
        return 0.0


def calculate_impermanent_loss(
    price_change_a: float,
    price_change_b: float
) -> float:
    """Calculate impermanent loss for LP positions."""
    if price_change_a <= 0 or price_change_b <= 0:
        return 0.0
    
    price_ratio = price_change_a / price_change_b
    il = 2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1
    return abs(il) * 100  # Return as percentage


def optimize_gas_strategy(
    operations: List[Dict[str, Any]],
    max_gas_budget: float = 100.0
) -> Dict[str, Any]:
    """Optimize transaction sequencing for gas efficiency."""
    # Simple gas optimization strategy
    # In practice, this would consider current network fees and operation complexity
    
    # Sort operations by estimated efficiency
    sorted_ops = sorted(operations, key=lambda x: x.get("estimated_cost", 0))
    
    total_cost = sum(op.get("estimated_cost", 0) for op in sorted_ops)
    
    if total_cost <= max_gas_budget:
        return {
            "strategy": "batch_all",
            "operations": sorted_ops,
            "total_cost": total_cost,
            "optimization": "All operations can be executed within budget"
        }
    else:
        # Select subset that fits budget
        selected_ops = []
        running_cost = 0.0
        
        for op in sorted_ops:
            op_cost = op.get("estimated_cost", 0)
            if running_cost + op_cost <= max_gas_budget:
                selected_ops.append(op)
                running_cost += op_cost
            else:
                break
        
        return {
            "strategy": "prioritized_subset",
            "operations": selected_ops,
            "deferred_operations": sorted_ops[len(selected_ops):],
            "total_cost": running_cost,
            "optimization": f"Selected {len(selected_ops)}/{len(sorted_ops)} operations within budget"
        }