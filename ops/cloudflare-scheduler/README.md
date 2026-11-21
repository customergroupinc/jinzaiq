# JINZAiQ の外部定時起動（準備段階）

## 目的
GitHub Actions の `schedule` に大幅な遅延・実行漏れが発生したため、Cloudflare Workers の Cron Triggers から `workflow_dispatch` を呼び出す追加経路を設ける。

**このリポジトリへのコード追加だけでは外部定時起動は開始しない。Cloudflare 側の作成・デプロイ・Secret 設定・Cron 設定が必要。**

## 事前準備
1. Cloudflare Workers を使用できるアカウントを用意する。
2. GitHub で Fine-grained personal access token を作る。Repository access は `customergroupinc/jinzaiq` だけに制限し、Repository permissions の **Actions: Read and write** のみを追加する。短めの有効期限を設定する。
3. トークンはチャット・GitHub・スクリーンショットに貼らず、Cloudflare Worker の **Secret `GITHUB_TOKEN`** にのみ登録する。トークンを環境変数の通常の公開値、コード、URLパラメータに入れない。

## デプロイ
Cloudflare Workers に `worker.js` を登録し、Cron Trigger を `7 3,9,21 * * *`（UTC）に設定する。Wrangler を使う場合はこのディレクトリからデプロイできる。スケジュール設定の反映には時間がかかる場合がある。

GitHub 側のワークフローには `workflow_dispatch.inputs.trigger_source` を追加済み。Cloudflare は
`POST https://api.github.com/repos/customergroupinc/jinzaiq/actions/workflows/update-news.yml/dispatches`
に `{"ref":"main","inputs":{"trigger_source":"cloudflare"}}` を送る。

Cloudflare が受け取る HTTP 204 は「GitHubが起動要求を受理した」ことだけを示す。**ニュースの更新成功やGitHub Pages公開完了を意味しない。**

## 本番にする前の必須テスト
1. Cloudflare Workers のテスト機能で `scheduled()` を実行し、Worker のログで GitHub HTTP 204 を確認する。
2. GitHub Actions に新しい `workflow_dispatch` 実行が作成され、更新ジョブが成功していることを確認する。
3. GitHub Actions の成功ログから HTML生成、mainへのPushを確認する。
4. GitHub Pages の公開ページで最終更新時刻が進んだことを確認する。
5. Healthchecks.io の対象チェックが `Up` になることを確認し、通知先Slack連携のテスト通知を実行する。
6. 実際の 06:07 / 12:07 / 18:07 JST のうち少なくとも1枠で自動起動・公開更新・監視を観測する。

## 当面の注意
GitHub 内蔵 schedule は変更・削除していない。外部スケジュール設定が成功すると両方の経路から起動して**重複実行になる可能性がある**。実動作が確認できてからGitHub内蔵の予定をバックアップ時刻へずらし、最新公開時刻を見て不要な再収集をスキップする仕組みを別PRで導入する。

Healthchecks.io への成功Pingは `schedule` および `trigger_source=cloudflare` の成功時のみで、通常の手動実行は監視を正常化しない。

GitHub API tokenの漏えいを疑った場合は直ちにGitHub側で無効化する。

## 参考
- https://developers.cloudflare.com/workers/configuration/cron-triggers/
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- https://healthchecks.io/docs/
