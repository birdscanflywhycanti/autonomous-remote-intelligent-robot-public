"""Script to stop the motors on the robot"""
import ThunderBorg3 as ThunderBorg

TB = ThunderBorg.ThunderBorg()
TB.Init()
TB.MotorsOff()
print("Stopped")
