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

    bool empty() const {
        return top == nullptr;
    }

    Token peek() const {
        if (empty()){
            throw std::underflow_error("Stack is empty");
        }
        return top->data;
    }

    void push(Token t){
        node* newNode = new node{t, top};
        top = newNode;
    }

    void pop() {
        if (empty()){
            throw std::underflow_error("Stack is empty");
        }
        node* temp = top;
        top = top->next;
        delete temp; 
    }
};


struct tree_node{
    Token data;
    tree_node* left;
    tree_node* right;
};

std::vector<Token> split(const std::string& s){
    std::vector<Token> tokens;
    for (std::string::size_type i = 0; i < s.size(); i++){
        char ch = s[i];

        if (std::isspace(static_cast<unsigned char>(ch))){
            continue;
        }

        if (std::isalpha(static_cast<unsigned char>(ch))){
            tokens.push_back(ch);
            continue;
        }

        if (std::isdigit(static_cast<unsigned char>(ch))){
            int num = 0;

            while(
                i < s.size() &&
                std::isdigit(static_cast<unsigned char>(s[i]))
            ){
                num = num * 10 + (s[i] - '0');
                ++i;
            }

            tokens.push_back(num);
            --i;
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
        throw std::invalid_argument(std::string("Invalid character: ") + ch);
    }
    return tokens;
}


int priority(char op){
    if (op == '+' || op == '-'){
        return 1;
    }
    if (op == '*' || op == '/'){
        return 2;
    }
    return 0;
}


std::vector<Token> formula_stack(stack& FStack, const std::vector<Token>& TokenList){
    std::vector<Token> postfix;

    for (const Token& token : TokenList){
        if (
            std::holds_alternative<int>(token) ||
            std::isalpha(static_cast<unsigned char>(std::get<char>(token)))
        ){
            postfix.push_back(token);
            continue;
        }

        char op = std::get<char>(token);

        if (op == '('){
            FStack.push(op);
        }
        else if (op == ')'){
            while(
                !FStack.empty() &&
                std::get<char>(FStack.peek()) != '('
            ){
                postfix.push_back(FStack.peek());
                FStack.pop();
            }

            if (FStack.empty()){
                throw std::invalid_argument("Mismatched parentheses");
            }
            FStack.pop();
        }
        else{
            while(
                !FStack.empty() &&
                std::get<char>(FStack.peek()) != '(' &&
                priority(std::get<char>(FStack.peek())) >= priority(op)
            ){
                postfix.push_back(FStack.peek());
                FStack.pop();
            }
            FStack.push(op);
        }
    }

    while(!FStack.empty()){
        char op = std::get<char>(FStack.peek());
        if (op == '('){
            throw std::invalid_argument("Mismatched parentheses");
        }
        postfix.push_back(FStack.peek());
        FStack.pop();
    }

    return postfix;
}





tree_node* build_tree(const std::vector<Token>& postfix){
    std::vector<tree_node*> TreeStack;

    for (const Token& token : postfix){
        if (
            std::holds_alternative<int>(token) ||
            std::isalpha(static_cast<unsigned char>(std::get<char>(token)))
        ){
            TreeStack.push_back(new tree_node{token, nullptr, nullptr});
            continue;
        }

        if (TreeStack.size() < 2){
            throw std::invalid_argument("Invalid expression");
        }

        tree_node* right = TreeStack.back();
        TreeStack.pop_back();
        tree_node* left = TreeStack.back();
        TreeStack.pop_back();

        TreeStack.push_back(new tree_node{token, left, right});
    }

    if (TreeStack.size() != 1){
        throw std::invalid_argument("Invalid expression");
    }

    return TreeStack.back();
}


void print_token(const Token& token){
    if (std::holds_alternative<int>(token)){
        std::cout << std::get<int>(token) << ' ';
    }
    else{
        std::cout << std::get<char>(token) << ' ';
    }
}


void postorder(tree_node* root){
    if (root == nullptr){
        return;
    }

    postorder(root->left);
    postorder(root->right);
    print_token(root->data);
}


void destroy_tree(tree_node* root){
    if (root == nullptr){
        return;
    }

    destroy_tree(root->left);
    destroy_tree(root->right);
    delete root;
}


int main(){
    std::string expression;
    std::getline(std::cin, expression);

    try{
        std::vector<Token> TokenList = split(expression);
        stack FStack;
        std::vector<Token> postfix = formula_stack(FStack, TokenList);

        std::cout << "Postfix: ";
        for (const Token& token : postfix){
            print_token(token);
        }
        std::cout << '\n';

        tree_node* root = build_tree(postfix);
        std::cout << "Postorder: ";
        postorder(root);
        std::cout << '\n';

        destroy_tree(root);
    }
    catch(const std::exception& error){
        std::cerr << error.what() << '\n';
        return 1;
    }

    return 0;
}
