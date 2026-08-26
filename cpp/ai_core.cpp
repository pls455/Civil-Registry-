#include <algorithm>
#include <cctype>
#include <sstream>
#include <string>
#include <vector>

// Lightweight native text core. It is intentionally dependency-free so it can
// be compiled on Android/Termux with clang++ and used alongside Python.
std::vector<std::string> tokenize(const std::string& text) {
    std::vector<std::string> out;
    std::istringstream in(text);
    std::string word;
    while (in >> word) {
        std::transform(word.begin(), word.end(), word.begin(),
                       [](unsigned char c){ return std::tolower(c); });
        if (word.size() > 1) out.push_back(word);
    }
    return out;
}

int overlap_score(const std::string& a, const std::string& b) {
    auto x = tokenize(a), y = tokenize(b);
    int score = 0;
    for (const auto& i : x)
        for (const auto& j : y)
            if (i == j) ++score;
    return score;
}

int main() { return 0; }
