#include <iostream>
#include <algorithm>

// Type::xxx 枚举值
enum class Type{
    UInt16,
    UInt32,
    FP32,
};


class ObjectT{
    private:
        std::string name;
        Type dtype;
        int data;
    public:
        ObjectT(std::string name, Type dtype, int data){
            this->name = name;
            this->dtype = dtype;
            this->data = data;
        }
        const char* typeName(Type type) const{
            switch (type) {
                case Type::UInt16: return "UInt16";
                case Type::UInt32: return "UInt32";
                case Type::FP32:   return "FP32";
            }
            return "Unknown";
        }
        void PrintInfo() const{
            std::cout << "===" << std::endl;
            std::cout << "Name:" << this->name << std::endl;
            std::cout << "dtype:" << typeName(this->dtype) << std::endl;
            std::cout << "data:" << data << std::endl;
        }
};


int main(){
    ObjectT obj("example",Type::UInt16,1);
    obj.PrintInfo();
    return 0;
}