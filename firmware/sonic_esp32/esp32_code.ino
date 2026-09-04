#include <driver/i2s.h>

const int txPin = 19; 
const int rxPin = 34; 

#define I2S_PORT I2S_NUM_0
const int SAMPLE_RATE = 200000; 
const int NUM_SAMPLES = 600;   
uint16_t adc_buffer[NUM_SAMPLES]; 

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 2,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_adc_mode(ADC_UNIT_1, ADC1_CHANNEL_6);
}

void setup() {
  Serial.begin(115200);
  pinMode(txPin, OUTPUT);
  
  ledcSetup(0, 40000, 8); 
  ledcAttachPin(txPin, 0);
  ledcWrite(0, 0); 
  
  setupI2S();
}

void loop() {
  // Wait patiently until Python sends a command over the USB cable
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // If Python sends the number 1, execute the capture
    if (command == '1') {
      
      // 1. MIC ON
      i2s_adc_enable(I2S_PORT);

      // 2. FIRE PING
      ledcWrite(0, 127);         
      delayMicroseconds(200);    
      ledcWrite(0, 0);           
      digitalWrite(txPin, LOW);  

      // 3. CAPTURE
      size_t bytes_read;
      i2s_read(I2S_PORT, &adc_buffer, NUM_SAMPLES * sizeof(uint16_t), &bytes_read, portMAX_DELAY);

      // 4. MIC OFF
      i2s_adc_disable(I2S_PORT);

      // 5. DUMP DATA
      Serial.println("START"); 
      for (int i = 0; i < NUM_SAMPLES; i++) {
        uint16_t clean_reading = adc_buffer[i] & 0x0FFF; 
        Serial.println(clean_reading);
      }
      Serial.println("END");
    }
  }
}