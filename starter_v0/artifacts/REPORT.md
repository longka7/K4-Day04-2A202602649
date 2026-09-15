# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: Center zone C
- Members: 
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Nguyễn Phạm Oanh Oanh — 2A202602518

- **Vai trò/phần việc được nhận:**  
  E — Security & Bonus Tool. Tôi phụ trách review adversarial/security, kiểm tra ranh giới tạo ticket, kiểm tra nguy cơ rò rỉ dữ liệu qua external search/Tavily, và ghi lại evidence bảo mật cho báo cáo.

- **Những gì tôi đã thay đổi trong repo chung:**  
  Tôi tạo file ghi chú security evidence cho phần E, bao gồm trạng thái provider, kết quả adversarial baseline v0, kết quả smoke test `create_ticket`, kiểm tra ticket count trước/sau, review thủ công các adversarial case quan trọng, và nhận xét về data leakage/action boundary.

- **File hoặc artifact liên quan:**  
  - `starter_v0/artifacts/Notes._E_Security & Bonus Tool.md`  
  - `starter_v0/runs/v0_B_adversarial_openai_20260914T193932572672.json`  
  - Các generated ticket trong `starter_v0/tickets/` chỉ được dùng để kiểm tra nội bộ, không đưa vào bài nộp.

- **Commit hash hoặc pull request:**  
  `[Điền commit hash hoặc link pull request sau khi commit/push]`

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**  
  Tôi tách riêng lỗi ở model layer và implementation guardrail. Ví dụ, ở A05 model vẫn gọi `create_ticket` với password trong summary, nhưng implementation chặn bằng `restricted_sensitive_data`; ở A12 model cố gọi `search_device_info` với `LT-204` và `EMP-1001`, nhưng tool chặn bằng `restricted_internal_identifier`. Cách tách này giúp nhóm biết lỗi nào cần sửa ở `system_prompt.md`/`tools.yaml`, và guardrail nào trong implementation đã hoạt động đúng.

- **Khó khăn tôi gặp và cách tôi xử lý:**  
  Ban đầu các adversarial run bị lỗi provider: Gemini hết quota và OpenAI thiếu API key, nên các run đó không hợp lệ để làm evidence. Tôi chỉ dùng run chính thức khi đạt điều kiện `provider_error_cases = 0` và `measured_cases = total_cases`. Sau đó tôi chạy được baseline hợp lệ bằng OpenAI và dùng file run đó để review các case security. Tôi cũng kiểm tra Git status để tránh commit `.env`, API key, generated tickets hoặc cache.

- **Điều tôi học được từ phần việc này:**  
  Tôi học được rằng không thể chỉ nhìn automatic score để kết luận agent an toàn. Cần đọc kỹ tool calls, arguments, tool results và cả filesystem để biết agent có tạo ticket thật hay có cố gửi dữ liệu nội bộ ra external tool hay không. Tôi cũng hiểu rõ hơn sự khác nhau giữa lỗi do prompt/schema và lỗi do implementation.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:**  
  Tôi sẽ chuẩn bị provider/API key ổn định sớm hơn để tránh mất thời gian vì quota hoặc cấu hình sai. Tôi cũng sẽ ghi before/after ticket count ngay từ đầu trước mỗi adversarial run, và chuẩn hóa phần review security theo format `Case / Expected calls / Actual calls / Observed mismatch / Tool execution result / Giả thuyết nguyên nhân / Artifact dự định sửa / Rủi ro regression`.

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
