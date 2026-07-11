# Example: Telegram Gateway Hung After Model Produced Refusal

Reproduction from a real incident (Jun 2026, deepseek/deepseek-v4-flash on OpenRouter).

## Symptoms

User reported: "my telegram seem not able to reach you?" — sent a message on Telegram and got no useful response.

## State File

gateway_state.json showed:
- pid: 7204, gateway_state: "running"
- telegram: "connected", no error_code
- platform updated_at: 4+ days stale (June 14, even though current date was June 18)
- The PID was still alive in /proc, but the process was hung

## Logs

s6 gateway log at `~/.hermes/logs/gateways/default/current`:
- Last entry was 4 days ago: "Skill 'hermes-vps-migration' updated."
- Nothing after that — gateway was alive but not processing or logging

## Session Trace (from state.db)

Latest Telegram session: `20260618_231337_0b027157` — still active (no ended_at).

The conversation:
1. User: "Weather today?" — triggered Taipei weather search (no location preference saved yet)
2. Assistant responded with Taipei weather
3. User: "Next time I ask you weather today please default it to east district hsinchu Taiwan"
4. Assistant saved to memory, confirmed
5. User: "Weather today?" — testing the preference
6. Assistant: "你好，我无法给与相关内容。" — model refusal/error in Chinese

After message #6 the session stayed active. The gateway process was alive but the model call loop was stuck — it never ended the session or moved to the next user message.

## Root Cause

The model `deepseek/deepseek-v4-flash` through OpenRouter produced a refusal on the second weather query (after the preference was just saved). This appears to be a model/provider issue — the model refused to answer or the response was malformed. The gateway received the broken response but then hung on that session instead of completing it.

The real failure was model-side, not Telegram-side. The Telegram platform itself was connected and functional.

## Fix

Restart the gateway to unstick it from the hung session. This lets s6 respawn a fresh process that can accept new messages. Then consider switching to a more reliable model.