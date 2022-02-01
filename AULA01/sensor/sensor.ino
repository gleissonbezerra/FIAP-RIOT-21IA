#define vref 5.0

void setup()
{
	pinMode(A0,INPUT);
	Serial.begin(9600);
}

void loop()
{
  
	int value = analogRead(A0);
	float voltage = ((float)value/1024) * vref;
	float tmpCel = (voltage-0.5) * 100;

	Serial.print("Celsius: ");
	Serial.println(tmpCel);

	delay(1000);

}