[2025-10-20T16:02:22Z] 🔄 GitHub sync started
[2025-10-20T16:02:23Z] ✅ git config user.name "ConsensusBot"

[2025-10-20T16:02:23Z] ✅ git config user.email "rafa1215@users.noreply.github.com"

[2025-10-20T16:02:36Z] ✅ git add -A

[2025-10-20T16:02:41Z] ✅ git commit -m "Automated sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
[v1.1-dev 82d68716] Automated sync: 2025-10-20T16:02:36Z
 75 files changed, 8872 insertions(+), 3989 deletions(-)
 create mode 100644 memory/logs/agents/evolution/evolution_run_2025-10-20.json
 delete mode 100644 memory/logs/agi/evolution_log.md
 create mode 100644 memory/logs/agi/reasoning_log.md
 rename memory/logs/{status/2025-W42-status.md => archive/2025-W43-status.md} (69%)
 rename memory/logs/{security => archive}/audit_report_20251019.md (100%)
 rename memory/logs/{finance => archive}/bills_2025-10-19.md (100%)
 rewrite memory/logs/archive/daily_summary.md (64%)
 rename memory/logs/{fitness => archive}/fitness_summary_20251019.md (100%)
 create mode 100644 memory/logs/archive/fitness_summary_20251020.md
 rewrite memory/logs/archive/github_sync_log.md (91%)
 rename memory/logs/{media => archive}/media_2025-10-19.md (100%)
 rename memory/logs/{status => archive}/progress_evaluation_20251019.md (100%)
 rewrite memory/logs/email/daily_summary.md (85%)
 create mode 100644 memory/logs/finance/bills_2025-10-20.md
 create mode 100644 memory/logs/fitness/fitness_data_20251020.json
 create mode 100644 memory/logs/fitness/insights/fitness_insight_2025-10-20.txt
 delete mode 100644 memory/logs/fitness/latest_fitness.md
 delete mode 100644 memory/logs/health/health_intelligence.md
 create mode 100644 memory/logs/media/media_2025-10-20.md
 create mode 100644 memory/logs/media/movie_recommendations/weekly_list_2025-10-20.md
 rewrite memory/logs/scheduler/state.json (81%)
 create mode 100644 memory/logs/security/audit_report_20251020.md
 create mode 100644 memory/logs/sms_guard/log_2025-10-20.txt
 create mode 100644 memory/logs/status/2025-W43-status.md
 create mode 100644 memory/logs/status/progress_evaluation_20251020.md
 create mode 100644 memory/logs/system/agent_summaries/agent_expansion_update_2025-10-20_0902.md
 rename memory/logs/system/agent_summaries/{ => archive}/agent_expansion_update_2025-10-17_0902.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_brainstorm_2025-10-17_0902.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_optimization_2025-10-17_0902.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/top10_suggestions_2025-10-17_0902.md (100%)
 rename memory/logs/system/agent_summaries/{ => archive}/unused_files_2025-10-17.md (100%)
 create mode 100644 memory/logs/system/agent_summaries/top10_brainstorm_2025-10-20_0902.md
 create mode 100644 memory/logs/system/agent_summaries/top10_optimization_2025-10-20_0902.md
 create mode 100644 memory/logs/system/agent_summaries/top10_suggestions_2025-10-20_0902.md
 create mode 100644 memory/logs/system/agent_summaries/unused_files_2025-10-20.md
 create mode 100644 memory/logs/system/audit/reality_audit_2025-10-20.json
 create mode 100644 memory/logs/system/integration_manifest_2025-10-20.json
 create mode 100644 memory/logs/system/project_status/final_status_2025-10-20.md
 create mode 100644 memory/logs/system/recursive_ai/recursive_ai_update_2025-10-20.json
[2025-10-20T16:02:50Z] ⚠️ Attempt 1: git push origin v1.1-dev
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V09XfgPYEaI4t05bajp5SSY        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:          - commit: f32bac16701765cfdc53dae8154d794022c385e9        
remote:            path: memory/core/secrets/token_gmail.json:5        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V1dcdF5DR8XTFbsaE5ilJqn        
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V0nxqSu3FLHYwrlRyRHz9tn        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V2vzs2pisLMEaKZWQ51CVdW        
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V6U3unQVMMTLNhIXEL70EDF        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      4 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-20T16:03:03Z] ⚠️ Attempt 2: git push origin v1.1-dev
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V09XfgPYEaI4t05bajp5SSY        
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V0nxqSu3FLHYwrlRyRHz9tn        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:          - commit: f32bac16701765cfdc53dae8154d794022c385e9        
remote:            path: memory/core/secrets/token_gmail.json:5        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V1dcdF5DR8XTFbsaE5ilJqn        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V2vzs2pisLMEaKZWQ51CVdW        
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V6U3unQVMMTLNhIXEL70EDF        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      4 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-20T16:03:13Z] ⚠️ Attempt 3: git push origin v1.1-dev
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V09XfgPYEaI4t05bajp5SSY        
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
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V0nxqSu3FLHYwrlRyRHz9tn        
remote:             
remote:             
remote:       —— Google OAuth Client ID ————————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:          - commit: f32bac16701765cfdc53dae8154d794022c385e9        
remote:            path: memory/core/secrets/token_gmail.json:5        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V1dcdF5DR8XTFbsaE5ilJqn        
remote:             
remote:             
remote:       —— Google OAuth Refresh Token ————————————————————————        
remote:        locations:        
remote:          - commit: f67fb95c114fa5b952f99d1473cd273a1f0ab315        
remote:            path: secrets/google_token.json:1        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8V2vzs2pisLMEaKZWQ51CVdW        
remote:             
remote:             
remote:       —— Google OAuth Client Secret ————————————————————————        
remote:        locations:        
remote:          - commit: d0bf050f23ecc6b1d27923b4f8be931eddcc1bec        
remote:            path: memory/core/secrets/gmail_credentials.json:1        
remote:          - commit: f32bac16701765cfdc53dae8154d794022c385e9        
remote:            path: memory/core/secrets/token_gmail.json:6        
remote:             
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.        
remote:        https://github.com/rafa8525/consensus-project/security/secret-scanning/unblock-secret/34I8XOVlOCbCNQas8osrk29W6K9        
remote:             
remote:             
remote:     ——[ WARNING ]—————————————————————————————————————————        
remote:      4 more secrets detected. Remove each secret from your commit history to view more detections.        
remote:      https://docs.github.com/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/excluding-folders-and-files-from-secret-scanning        
remote:     ——————————————————————————————————————————————————————        
remote: 
remote: 
To https://github.com/rafa8525/consensus-project.git
 ! [remote rejected]   v1.1-dev -> v1.1-dev (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/rafa8525/consensus-project.git'
[2025-10-20T16:03:18Z] ❌ GitHub sync failed after retries
