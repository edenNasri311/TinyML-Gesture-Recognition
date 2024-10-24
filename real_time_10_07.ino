#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <M5StickCPlus.h>
#include <tensorflow/lite/model.h>
 
const float accelerationThreshold = 2.5; // threshold of significant in G's
const int numSamples = 70;
int samplesRead = numSamples;
 
// global variables used for TensorFlow Lite (Micro)
tflite::ErrorReporter* error_reporter = nullptr;
 
// pull in all the TFLM ops, you can remove this line and
// only pull in the TFLM ops you need, if would like to reduce
// the compiled size of the sketch.
tflite::AllOpsResolver tflOpsResolver;
 
const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;
 
// Create a static memory buffer for TFLM, the size may need to
// be adjusted based on the model you are using
constexpr int tensorArenaSize = 8 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));
 
// array to map gesture index to a name
const char* GESTURES[] = {
  "up",
  "down",
};

#define NUM_GESTURES (sizeof(GESTURES) / sizeof(GESTURES[0]))
void setup() {
 
  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;
 
  M5.begin();
  M5.Lcd.setRotation(3);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(2);  // Set font size.  设置字体大小
 
  M5.IMU.Init();  
 
  Serial.begin(115200);
 
  // get the TFL representation of the model byte array
  tflModel = tflite::GetModel(model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    while (1);
  }
 
  // Create an interpreter to run the model
  tflInterpreter = new tflite::MicroInterpreter(tflModel, tflOpsResolver, tensorArena, tensorArenaSize, error_reporter);
 
  // Allocate memory for the model's input and output tensors
  tflInterpreter->AllocateTensors();
 
  // Get pointers for the model's input and output tensors
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);
}
 
void loop() {
  float aX, aY, aZ, gX, gY, gZ;
 
  // wait for significant motion
  while (samplesRead == numSamples) {
      // read the acceleration data
    M5.IMU.getAccelData(&aX, &aY, &aZ);
 
      // sum up the absolutes
      float aSum = fabs(aX) + fabs(aY) + fabs(aZ);
 
      // check if it's above the threshold
      if (aSum >= accelerationThreshold) {
        // reset the sample read count
        samplesRead = 0;
        break;
      }
  }
 
  // check if the all the required samples have been read since
  // the last time the significant motion was detected
  while (samplesRead < numSamples) {
    // check if new acceleration AND gyroscope data is available
      // read the acceleration and gyroscope data
      M5.IMU.getAccelData(&aX, &aY, &aZ);
      M5.IMU.getGyroData(&gX,&gY,&gZ);
 
 
      // normalize the IMU data between 0 to 1 and store in the model's
      // input tensor
      tflInputTensor->data.f[samplesRead * 6 + 0] = (aX + 5.0) / 10.0;
      tflInputTensor->data.f[samplesRead * 6 + 1] = (aY + 5.0) / 10.0;
      tflInputTensor->data.f[samplesRead * 6 + 2] = (aZ + 5.0) / 10.0;
      tflInputTensor->data.f[samplesRead * 6 + 3] = (gX + 100.0) / 200.0;
      tflInputTensor->data.f[samplesRead * 6 + 4] = (gY + 100.0) / 200.0;
      tflInputTensor->data.f[samplesRead * 6 + 5] = (gZ + 100.0) / 200.0;
 
      samplesRead++;
 
      if (samplesRead == numSamples) {
        // Run inferencing
        TfLiteStatus invokeStatus = tflInterpreter->Invoke();
        if (invokeStatus != kTfLiteOk) {
          Serial.println("Invoke failed!");
          while (1);
          return;
        }
 
        // Loop through the output tensor values from the model
        for (int i = 0; i < NUM_GESTURES; i++) {
          if  ((tflOutputTensor->data.f[i])>0.9 & i==1){
          Serial.print(GESTURES[i]);
          Serial.print(": ");
          Serial.println(tflOutputTensor->data.f[i], 6);
          M5.Lcd.setCursor(0, 0);
          }
          if(tflOutputTensor->data.f[i]>0.9){
            if(i == 0){

              M5.Lcd.println("       \n              ");
              M5.Lcd.println("Gesture\nRecognized: up");  
             Serial.printf("Gesture\nRecognized: up\n");                                      
            }
            else if(i == 1){
              M5.Lcd.println("       \n                ");    
              M5.Lcd.println("Gesture\nRecognized: down");
              Serial.printf("Gesture\nRecognized: down\n");                                      

            }
          }
        }
        Serial.println();
      }
  }

}