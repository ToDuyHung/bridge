# Paper Recommendation & Citation Recommendation Research

Tài liệu này tổng hợp các mô hình và kỹ thuật State-of-the-art (SOTA) trong bài toán gợi ý bài báo khoa học (Paper Recommendation) và gợi ý trích dẫn (Citation Recommendation), tập trung vào các tập dữ liệu học thuật như DBLP-Citation-network V18.

## 1. Bảng Khảo sát các Mô hình SOTA (2022 - 2024+)

Dưới đây là các phương pháp hàng đầu được phân loại theo kiến trúc và hiệu năng benchmark.

| Mô hình / Kiến trúc | Paper / Blog | Code | Xử lý Input | Label Output | Loss Function | Năm | Danh mục |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LlamaRec** | [Link](https://arxiv.org/abs/2311.02089) | [GitHub](https://github.com/Yueeeeeeee/LlamaRec) | Title + Abst + User History | Ranking Logits | Cross-Entropy | 2024 | LLM-based |
| **SPECTER 2.0** | [Link](https://arxiv.org/abs/2211.13327) | [GitHub](https://github.com/allenai/SPECTER2) | Title + [SEP] + Abstract | Triplet (Q, P, N) | Triplet Margin | 2023 | Text-based |
| **OAG-BERT v2** | [Link](https://arxiv.org/abs/2203.00392) | [GitHub](https://github.com/THUDM/CogDL) | Text + Entity (Author, Venue) | Link Prediction | MLM + Alignment | 2023 | Hybrid KG |
| **SciNCL** | [Link](https://arxiv.org/abs/2202.06671) | [GitHub](https://github.com/malteos/scincl) | Title + Abstract + Neighbors | Graph Contrastive | InfoNCE | 2022 | Contrastive |
| **LinkBERT** | [Link](https://arxiv.org/abs/2203.15827) | [GitHub](https://github.com/michiyasunaga/LinkBERT) | Multiple Linked Docs | Relation Prediction | MLM + DRP | 2022 | Relation-aware |
| **ProSAGE** | [Link](https://paperswithcode.com/task/citation-recommendation) | [GitHub](https://github.com/pyg-team/pytorch_geometric) | Node Specs + Adjacency | Link Exist (0/1) | BPR / BCE | 2022 | Graph-based |

## 2. Quy trình xử lý dữ liệu (DBLP/AMiner)

### Xử lý Input
*   **Textual Features**: Concatenate `Title` và `Abstract` (phổ biến nhất).
*   **Meta-data**: `Authors`, `Venue`, `Year`, `Keywords` được mã hóa thành thực thể (Entities) hoặc đặc trưng bổ sung.
*   **Structural Features**: Xây dựng đồ thị trích dẫn (Citation Graph) từ trường `references`.

### Labeling & Loss
*   **Triplet Sampling**: Lấy 1 paper gốc (Anchor), 1 paper được trích dẫn (Positive) và 1 paper ngẫu nhiên (Negative). Chiến lược "Hard Negative Mining" thường cho kết quả tốt nhất.
*   **Contrastive Loss (InfoNCE)**: So sánh anchor với nhiều ứng viên đồng thời, giúp mô hình phân biệt tốt các paper có nội dung tương đồng nhưng không có quan hệ trích dẫn.

## 3. Khuyến nghị thực hiện

> [!TIP]
> **Chiến lược tối ưu**: Sử dụng phương pháp **Two-stage Recommendation**:
> 1. **Retrieval Stage**: Dùng mô hình Embedding nhanh (như SPECTER 2.0) để lấy ra Top-100 ứng viên.
> 2. **Ranking Stage**: Dùng LLM (như LlamaRec hoặc GPT-4) để xếp hạng lại (Re-rank) dựa trên ngữ cảnh chi tiết.

---
*Dữ liệu khảo sát dựa trên các benchmark công khai (SCIDOCS, DBLP, PubMed).*
