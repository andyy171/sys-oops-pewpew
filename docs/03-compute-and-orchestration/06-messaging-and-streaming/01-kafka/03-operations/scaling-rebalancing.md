# Scaling và Rebalancing trong Kafka

Scaling và rebalancing là hai khía cạnh quan trọng trong việc quản lý và vận hành một cluster Kafka. Chúng giúp đảm bảo rằng hệ thống có thể mở rộng để đáp ứng nhu cầu tăng trưởng và duy trì hiệu suất ổn định khi có sự thay đổi trong cấu hình hoặc tải.

## Scaling trong Kafka
Scaling trong Kafka đề cập đến việc thêm hoặc bớt các broker trong cluster để đáp ứng nhu cầu tăng trưởng hoặc giảm tải. Khi bạn thêm một broker mới vào cluster, Kafka sẽ tự động phân phối lại các partition và replicas để tận dụng tài nguyên mới và đảm bảo rằng dữ liệu được lưu trữ và phục vụ một cách hiệu quả. Ngược lại, khi bạn loại bỏ một broker, Kafka cũng sẽ tự động phân phối lại các partition và replicas để đảm bảo rằng dữ liệu vẫn được phục vụ một cách ổn định.

## Rebalancing trong Kafka
Rebalancing trong Kafka xảy ra khi có sự thay đổi trong cấu hình của cluster, chẳng hạn như khi một broker mới được thêm vào hoặc một broker bị loại bỏ. Khi rebalancing xảy ra, Kafka sẽ tự động phân phối lại các partition và replicas giữa các broker để đảm bảo rằng dữ liệu được lưu trữ và phục vụ một cách hiệu quả. Rebalancing cũng có thể xảy ra khi có sự thay đổi trong consumer group, chẳng hạn như khi một consumer mới tham gia hoặc một consumer bị loại bỏ. Trong trường hợp này, Kafka sẽ tự động phân phối lại các partition giữa các consumer để đảm bảo rằng dữ liệu được xử lý một cách hiệu quả.