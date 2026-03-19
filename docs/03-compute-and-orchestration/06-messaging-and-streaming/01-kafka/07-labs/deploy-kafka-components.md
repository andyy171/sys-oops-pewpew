# Lab - Triển khai các thành phần Kafka


Chuẩn bị : 
- Một hệ thống Linux-based

1. Cài đặt Kafka
Apache Kafka khả dụng đẻ tải từ trang web chính thức của nó . Tuy nhiên, để đơn giản , ta dùng curl để tải trực tiếp Kafka binary từ trang web chính thức của nó. Bạn có thể sử dụng lệnh sau để tải Kafka binary:

```bash
curl -L https://downloads.apache.org/kafka/3.7.1/kafka_2.13-3.7.1.tgz -o ~/Downloads/kafka.tgz
```

2. Extracting
```bash
mkdir ~/kafka && cd ~/kafka
tar -xvzf ~/Downloads/kafka.tgz --strip 1 -C ~/kafka

```

3. Setting Zookeeper 
- Kafka sử dụng Zookeeper để quản lý cluster metadata và config. Mặc dù Kafka có swanx Zookeeper config , tuy nhiên chúng ta cần tạo một hệ thống dịch vụ cho Zookeepper để đảm bảo nó khởi động tự động cùng hệ thống .
    - Tạo file systemd service cho Zookeeper
    ```bash
    sudo tee /etc/systemd/system/zookeeper.service <<EOF
    [Unit]
    Requires=network.target remote-fs.target
    After=network.target remote-fs.target

    [Service]
    Type=simple
    User=root
    ExecStart=/root/kafka/bin/zookeeper-server-start.sh /root/kafka/config/zookeeper.properties
    ExecStop=/root/kafka/bin/zookeeper-server-stop.sh
    Restart=on-abnormal

    [Install]
    WantedBy=multi-user.target
    Save and close the editor (in nano, press CTRL+X, then Y, and Enter to save changes).
    EOF
    ```
4. Setup Kafka Server 
```bash
sudo tee /etc/systemd/system/kafka.service <<EOF
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=root
ExecStart=/bin/sh -c '/root/kafka/bin/kafka-server-start.sh /root/kafka/config/server.properties > /root/kafka/kafka.log 2>&1'
ExecStop=/root/kafka/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF
```


5. Khởi động service
```bash
sudo systemctl enable zookeeper
sudo systemctl start zookeeper
sudo systemctl enable kafka
sudo systemctl start kafka
sudo systemctl status zookeeper
sudo systemctl status kafka
```

## Kafka Producer & Consumer
1. Khởi động Kafka (nếu chưa chạy)
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```
2. Tạo một topic mới
```bash
bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```
3. Kafka Producer
```bash
# Java Producer
# Tạo prooject
mkdir kafka-producer
cd kafka-producer
gradle init --type java-application
# Thêm dependency (build.gradle)
dependencies {
    implementation 'org.apache.kafka:kafka-clients:3.0.0'
}

## Producer Code 
import org.apache.kafka.clients.producer.*;
import java.util.Properties;

public class SimpleProducer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        Producer<String, String> producer = new KafkaProducer<>(props);

        String topic = "test-topic";

        producer.send(new ProducerRecord<>(topic, "key1", "Hello Kafka"));
        producer.close();
    }
}

# Python Producer
mkdir kafka-producer
cd kafka-producer
python3 -m venv venv
source venv/bin/activate
pip install kafka-python

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=lambda k: k.encode(),
    value_serializer=lambda v: v.encode()
)

producer.send('test-topic', key='key1', value='Hello Kafka')
producer.close()
```

4. Kafka Consumer
```bash
# Java Consumer
# Tạo prooject
mkdir kafka-consumer
cd kafka-consumer
gradle init --type java-application
# Thêm dependency (build.gradle)
dependencies {
    implementation 'org.apache.kafka:kafka-clients:2.8.0'
}

## Consumer Code
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.*;

public class SimpleConsumer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("group.id", "test-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("auto.offset.reset", "earliest");

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList("test-topic"));

        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> r : records) {
                System.out.println(r.value());
            }
        }
    }
}

# Python Consumer
mkdir kafka-consumer
cd kafka-consumer
python3 -m venv venv
source venv/bin/activate
pip install kafka-python

## Consumer Code
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='test-group',
    value_deserializer=lambda x: x.decode()
)

for msg in consumer:
    print(msg.value)
```

5. Test luồng hoạt động 
```bash
# Chạy consumer trước
java SimpleConsumer
# hoặc
python consumer.py

# Sau đó chạy producer
java SimpleProducer
# hoặc
python producer.py


## Kết quả Consumer sẽ nhận và in ra message "Hello Kafka"
```
