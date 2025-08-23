#!/usr/bin/env python3
"""
Fix Position Management - Make Trailing Stops Actually Work
"""

def fix_position_management():
    """Fix the position management to actually work on existing positions"""
    
    print("🔧 FIXING POSITION MANAGEMENT IN MAIN.PY")
    print("=" * 50)
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the trailing stop configuration
        old_config = '''# Trailing stop parameters
        self.trailing_start_profit = config.get('trailing_start_profit', 0.008)  # 0.8%'''
        
        new_config = '''# Trailing stop parameters - FIXED FOR EXISTING POSITIONS
        self.trailing_start_profit = config.get('trailing_start_profit', 0.002)  # 0.2% (much lower)'''
        
        content = content.replace(old_config, new_config)
        
        # Find and replace the management method to be more aggressive
        old_manage = '''def _manage_trailing_stop(self, position: ManagedPosition) -> Optional[TradeManagementAction]:
        """Manage trailing stop for 500 positions"""
        
        profit_pct = position.unrealized_pnl / (position.volume * 100000) if position.volume > 0 else 0
        
        if profit_pct >= self.trailing_start_profit:'''
        
        new_manage = '''def _manage_trailing_stop(self, position: ManagedPosition) -> Optional[TradeManagementAction]:
        """ENHANCED: Manage trailing stop for existing positions"""
        
        profit_pct = position.unrealized_pnl / (position.volume * 100000) if position.volume > 0 else 0
        
        # ENHANCED: More aggressive trailing for existing positions
        if profit_pct >= self.trailing_start_profit or position.unrealized_pnl > 5.0:  # $5+ profit or 0.2%'''
        
        content = content.replace(old_manage, new_manage)
        
        # Add debugging to position management
        old_management = '''# 3. Manage existing positions
                    management_actions = self.position_manager.manage_all_positions(self.last_signals)
                    
                    if management_actions:
                        print(f"🎯 POSITION MANAGEMENT: {len(management_actions)} actions taken")
                        for action in management_actions:
                            print(f"   • {action.value}")'''
        
        new_management = '''# 3. Manage existing positions - ENHANCED DEBUG
                    management_actions = self.position_manager.manage_all_positions(self.last_signals)
                    
                    # ENHANCED: Show management details
                    profitable_positions = [p for p in self.position_manager.managed_positions.values() if p.unrealized_pnl > 0]
                    if profitable_positions:
                        print(f"🔍 MANAGEMENT DEBUG: {len(profitable_positions)} profitable positions found")
                        for pos in profitable_positions[:5]:  # Show first 5
                            profit_pct = pos.unrealized_pnl / (pos.volume * 100000) if pos.volume > 0 else 0
                            print(f"   💰 {pos.symbol} ${pos.unrealized_pnl:.2f} ({profit_pct:.3%}) - Trailing: {'✅' if pos.trailing_stop_active else '❌'}")
                    
                    if management_actions:
                        print(f"🎯 POSITION MANAGEMENT: {len(management_actions)} actions taken")
                        for action in management_actions:
                            print(f"   • {action.value}")
                    else:
                        print(f"🔍 No management actions taken this iteration")'''
        
        content = content.replace(old_management, new_management)
        
        # Make the update_stop_loss method more robust
        old_update_sl = '''def _update_stop_loss(self, position: ManagedPosition, new_stop_loss: float) -> bool:
        """Update stop loss"""
        try:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": new_stop_loss,
                "tp": position.current_take_profit,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                position.current_stop_loss = new_stop_loss
                return True
            return False
        except:
            return False'''
        
        new_update_sl = '''def _update_stop_loss(self, position: ManagedPosition, new_stop_loss: float) -> bool:
        """ENHANCED: Update stop loss with better error handling"""
        try:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": new_stop_loss,
                "tp": position.current_take_profit,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                position.current_stop_loss = new_stop_loss
                print(f"✅ TRAILING STOP UPDATED: {position.symbol} #{position.ticket} SL: {new_stop_loss:.5f}")
                return True
            else:
                error_msg = result.comment if result else "Unknown error"
                print(f"⚠️ Failed to update SL for {position.symbol} #{position.ticket}: {error_msg}")
                return False
        except Exception as e:
            print(f"❌ Error updating SL for {position.symbol} #{position.ticket}: {e}")
            return False'''
        
        content = content.replace(old_update_sl, new_update_sl)
        
        # Write the fixed file
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Position management fixes applied!")
        print("\n🔧 CHANGES MADE:")
        print("   • Lowered trailing stop threshold: 0.8% → 0.2%")
        print("   • Added $5+ profit alternative trigger")
        print("   • Enhanced debugging for management actions")
        print("   • Better error handling for SL updates")
        print("   • Real-time management feedback")
        
        print("\n🚀 Now restart your bot to see active position management!")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")

if __name__ == "__main__":
    fix_position_management()
