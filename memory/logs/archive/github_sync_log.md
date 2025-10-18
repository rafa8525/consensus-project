[2025-10-17T16:02:38Z] 🔄 GitHub sync started
[2025-10-17T16:02:38Z] ✅ git config user.name "ConsensusBot"

[2025-10-17T16:02:38Z] ✅ git config user.email "rafa1215@users.noreply.github.com"

[2025-10-17T16:02:47Z] ✅ git add -A

[2025-10-17T16:02:50Z] ✅ git commit -m "Automated sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
[v1.1-dev d0bf050f] Automated sync: 2025-10-17T16:02:47Z
 88 files changed, 8398 insertions(+), 316 deletions(-)
 create mode 100644 memory/core/permanent/.do_not_delete
 create mode 100644 memory/core/permanent/core_manifest.yaml
 create mode 100644 memory/core/permanent/fitness_status.json
 create mode 100644 memory/core/permanent/geofence_activity_log.json
 create mode 100644 memory/core/permanent/last_absorption.txt
 create mode 100644 memory/core/permanent/purchase_log.json
 create mode 100644 memory/core/permanent/voice_timestamp_cache.json
 create mode 100644 memory/core/secrets/gmail_credentials.json
 create mode 100644 memory/logs/agents/evolution/evolution_run_2025-10-17.json
 rename memory/logs/{security => archive}/audit_report_20251016.md (100%)
 rename memory/logs/{fitness => archive}/fitness_summary_20251016.md (100%)
 rename memory/logs/{status => archive}/progress_evaluation_20251016.md (100%)
 create mode 100644 memory/logs/archive/vpn_test_report_20251016.md
 create mode 100644 memory/logs/finance/bills_2025-10-17.md
 create mode 100644 memory/logs/finance/finance_audit.md
 create mode 100644 memory/logs/finance/price_log.md
 create mode 100644 memory/logs/fitness/fitness_data_20251017.json
 create mode 100644 memory/logs/fitness/fitness_summary_20251017.md
 create mode 100644 memory/logs/fitness/insights/fitness_insight_2025-10-17.txt
 create mode 100644 memory/logs/media/media_2025-10-17.md
 create mode 100644 memory/logs/media/movie_recommendations/weekly_list_2025-10-17.md
 create mode 100644 memory/logs/progress/next_actions.md
 rewrite memory/logs/scheduler/state.json (81%)
 create mode 100644 memory/logs/security/audit_report_20251017.md
 create mode 100644 memory/logs/sms_guard/log_2025-10-17.txt
 create mode 100644 memory/logs/status/progress_evaluation_20251017.md
 create mode 100644 memory/logs/system/agent_summaries/agent_expansion_update_2025-10-16_1912.md
 create mode 100644 memory/logs/system/agent_summaries/agent_expansion_update_2025-10-17_0902.md
 rename memory/logs/system/agent_summaries/{ => archive}/agent_expansion_update_2025-10-15_2203.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/agent_expansion_update_2025-10-15_2223.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_brainstorm_2025-10-15_2203.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_brainstorm_2025-10-15_2223.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_optimization_2025-10-15_2203.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_optimization_2025-10-15_2223.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_suggestions_2025-10-15_2203.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_suggestions_2025-10-15_2223.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/unused_files_2025-10-14.md (100%)
 create mode 100644 memory/logs/system/agent_summaries/top10_brainstorm_2025-10-16_1912.md
 create mode 100644 memory/logs/system/agent_summaries/top10_brainstorm_2025-10-17_0902.md
 create mode 100644 memory/logs/system/agent_summaries/top10_optimization_2025-10-16_1912.md
 create mode 100644 memory/logs/system/agent_summaries/top10_optimization_2025-10-17_0902.md
 create mode 100644 memory/logs/system/agent_summaries/top10_suggestions_2025-10-16_1912.md
 create mode 100644 memory/logs/system/agent_summaries/top10_suggestions_2025-10-17_0902.md
 create mode 100644 memory/logs/system/agent_summaries/unused_files_2025-10-17.md
 create mode 100644 memory/logs/system/audit/reality_audit_2025-10-17.json
 create mode 100644 memory/logs/system/integration_manifest_2025-10-17.json
 create mode 100644 memory/logs/system/project_status/final_status_2025-10-17.md
 create mode 100644 memory/logs/system/recursive_ai/recursive_ai_update_2025-10-17.json
 create mode 100644 tools/gmail_auth_setup.py
 rewrite tools/master_control_loop.py (97%)
 create mode 100644 tools/permanent_layer_setup.py
 create mode 100644 tools/permanent_layer_verifier.py
[2025-10-17T16:02:53Z] ⚠️ Attempt 1: git push origin v1.1-dev
Uploading LFS objects: 100% (1/1), 1.7 MB | 0 B/s, done.
remote: error: GH013: Repository rule violations found for refs/heads/v1.1-dev.        
remote: 
remote: - GITHUB PUSH PROTECTION        
remote:   —————————————————————————————————————————        
remote:     Resolve the following violations before pushing again        
remote: 
remote:     - Push cannot contain secrets        
remote: 
remote:             
remote:      (?) Learn how to resolve a blocked push        
remote:      https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push        
remote:             
remote:      (?) This repository does not have Secret Scanning enabled, but is eligible. Enable Secret Scanning to view and manage detected secrets.        
remote:      Visit the repository settings page, https://github.com/rafa8525/consensus-project/settings/security_analysis        
remote:             
remote:             
remote:       —— Google OAuth Access Token —————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJJ2NcokZY1sqJRADN55QCcT        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_credentials.json:1        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJFAx9SghR3FbnqwMOjfsfJ2        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJIlhyRvCjbW6K0JA7uzy3Dd        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJDsa8Jx2IOPgBAExnTkxwTh        
remote:             
remote:             
remote:       —— Google OAuth Client Secret ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_credentials.json:1        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJK4C47OIolEV2xreEMN4rGG        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      1 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-17T16:03:00Z] ⚠️ Attempt 2: git push origin v1.1-dev
Uploading LFS objects: 100% (1/1), 1.7 MB | 0 B/s, done.
remote: error: GH013: Repository rule violations found for refs/heads/v1.1-dev.        
remote: 
remote: - GITHUB PUSH PROTECTION        
remote:   —————————————————————————————————————————        
remote:     Resolve the following violations before pushing again        
remote: 
remote:     - Push cannot contain secrets        
remote: 
remote:             
remote:      (?) Learn how to resolve a blocked push        
remote:      https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push        
remote:             
remote:      (?) This repository does not have Secret Scanning enabled, but is eligible. Enable Secret Scanning to view and manage detected secrets.        
remote:      Visit the repository settings page, https://github.com/rafa8525/consensus-project/settings/security_analysis        
remote:             
remote:             
remote:       —— Google OAuth Access Token —————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJJ2NcokZY1sqJRADN55QCcT        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_credentials.json:1        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJFAx9SghR3FbnqwMOjfsfJ2        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJIlhyRvCjbW6K0JA7uzy3Dd        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJDsa8Jx2IOPgBAExnTkxwTh        
remote:             
remote:             
remote:       —— Google OAuth Client Secret ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_credentials.json:1        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJK4C47OIolEV2xreEMN4rGG        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      1 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-17T16:03:09Z] ⚠️ Attempt 3: git push origin v1.1-dev
Uploading LFS objects: 100% (1/1), 1.7 MB | 0 B/s, done.
remote: error: GH013: Repository rule violations found for refs/heads/v1.1-dev.        
remote: 
remote: - GITHUB PUSH PROTECTION        
remote:   —————————————————————————————————————————        
remote:     Resolve the following violations before pushing again        
remote: 
remote:     - Push cannot contain secrets        
remote: 
remote:             
remote:      (?) Learn how to resolve a blocked push        
remote:      https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push        
remote:             
remote:      (?) This repository does not have Secret Scanning enabled, but is eligible. Enable Secret Scanning to view and manage detected secrets.        
remote:      Visit the repository settings page, https://github.com/rafa8525/consensus-project/settings/security_analysis        
remote:             
remote:             
remote:       —— Google OAuth Access Token —————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJJ2NcokZY1sqJRADN55QCcT        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_credentials.json:1        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJFAx9SghR3FbnqwMOjfsfJ2        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJIlhyRvCjbW6K0JA7uzy3Dd        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CUJDsa8Jx2IOPgBAExnTkxwTh        
remote:             
remote:             
remote:       —— Google OAuth Client Secret ————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34CULGLIFUBMryUAyAye5YMLo1Q        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      1 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-17T16:03:14Z] ❌ GitHub sync failed after retries
