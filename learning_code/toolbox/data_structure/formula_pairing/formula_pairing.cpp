#include<iostream>
#include<vector>
#include<variant>
#include<string>
#include<cctype>
#include<stdexcept>

#define STACK_CAPACITY 100

using Token = std::variant<char,int>;



struct node{
    Token data;
    node* next;
};

struct stack{
    std::vector<Token> list[STACK_CAPACITY];
    node* top = nullptr;

    void push(Token t){
        node* newNode = new node{t, top};
        top = newNode;
    }

    void pop() {
        if (top == nullptr){
            throw std::underflow_error("Stack is empty");
        }
        node* temp = top;
        top = top->next;
        delete temp; 
    }
};


std::vector<Token> split(const std::string& s){
    std::vector<Token> tokens;
    for (int i = 0; i < s.size(); i++){
        char ch = s[i];

        if (std::isspace(static_cast<unsigned char>(ch))){
            ++i;
            continue;
        }

        if (std::isdigit(static_cast<unsigned int>(ch))){
            int num = 0;

            while(
                i < s.size() &&
                std::isdigit(static_cast<unsigned int>(s[i]))
            ){
                num = num * 10 + (s[i] - '0');
                ++i;
            }

            tokens.push_back(ch);
            continue;
        }
        if (
            ch == '+'||
            ch == '-'||
            ch == '*'||
            ch == '/'||
            ch == '('||
            ch == ')'
        ){
            tokens.push_back(ch);
            continue;
        }
        throw std::invalid_argument(std::string("Invalid character:"+ ch));
    }
    return tokens;
}


void formula_stack(stack FStack, const std::vector<Token>& TokenList){
    

}
