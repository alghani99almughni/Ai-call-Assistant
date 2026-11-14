# India-first phone onboarding
Default UX: customer enters business name + Indian mobile number. Agent greets caller using the business name and answers from the tenant knowledge base by default. Advanced DID/operator/SIP is an optional separate route. Remove Twilio and international carrier integrations from product setup.

## Default: VoiceLink India
1. Customer completes VoiceLink account/KYC and gets an eligible Indian number.
2. Enter business name and E.164 +91 number in our portal.
3. Connect VoiceLink SIP/WebSocket to our voice agent; configure greeting and tenant knowledge retrieval.
4. Test incoming calls before going live.

VoiceLink advertises India numbers, SIP/WebSocket voicebot connectivity and carrier number management (https://voicelink.co.in/). Number allocation, channels, KYC and call minutes are provider-controlled and billable.

## Advanced: existing DID / operator
Customer with their own DID/SIP operator selects Advanced. Implement provider-specific trunk setup; SIP credentials belong in encrypted secrets, never plain tenant profile fields.

## Status
The tenant phone API saves business name, +91 mobile and provider selection. VoiceLink is default, custom SIP is optional. The inbound route is currently an event stub, NOT a live audio agent. Actual SIP/WebSocket bridge, local ASR/TTS, RAG audio loop, and end-to-end telephony testing remain before calls can be answered live.